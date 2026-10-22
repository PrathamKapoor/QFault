"""Independently recount a public historical recovery export archive, without replay.

The raw parser/interval reconstruction in audit_counterfactual is independent of
the engine decision functions. Nothing is extracted or executed from the archive.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

from qfault.evidence import digest
from qfault.storage import verify_export
from scripts.audit_counterfactual import audit_record

ROOT=Path(__file__).resolve().parents[1]


def verify(root):
    root=Path(root)
    errors=[]; policies={}; seen=set()
    try:
        manifest=json.loads((root/'manifest.json').read_bytes())
        if manifest.get('schema_version')!=1: raise ValueError('unsupported evidence schema')
        summary_path=root.parent/'counterfactual-recovery-holdout.json'
        raw=summary_path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=manifest['summary_sha256']:
            raise ValueError('historical summary byte digest mismatch')
        summary=json.loads(raw)
        archive=root/'reports.jsonl.gz'
        if archive.stat().st_size>32*1024*1024 or hashlib.sha256(archive.read_bytes()).hexdigest()!=manifest['reports_sha256']:
            raise ValueError('historical archive digest/size mismatch')
        expected={r['experiment_id']:r for r in summary['rows']}
        total_bytes=0
        with gzip.open(archive,'rb') as stream:
            while line:=stream.readline(16*1024*1024+1):
                total_bytes+=len(line)
                if len(line)>16*1024*1024 or total_bytes>256*1024*1024:
                    raise ValueError('historical archive expansion limit')
                bundle=json.loads(line)
                if not verify_export(bundle)['valid']: raise ValueError('invalid exported report')
                record=bundle['investigation']; eid=record['experiment_id']
                if eid in seen or eid not in expected: raise ValueError('duplicate/unmatched report')
                seen.add(eid); row=expected[eid]
                if digest(bundle['manifest'])!=row['manifest_sha256']: raise ValueError('summary manifest binding')
                audited=audit_record(record)
                for field in ('status','selected','eligible','discrepancy','plausible_loci'):
                    if row[field]!=audited[field]: raise ValueError('row mismatch: '+field)
                if row['cost']['shots']!=audited['shots'] or row['cost']['evaluations']!=audited['evaluations']:
                    raise ValueError('resource mismatch')
                policy=row['policy']
                if record['configuration']['selection_policy']!=policy: raise ValueError('policy mismatch')
                entry=policies.setdefault(policy,{'cases':0,'outcomes':Counter(),'shots':0,'evaluations':0})
                entry['cases']+=1; entry['outcomes'][audited['status']]+=1
                entry['shots']+=audited['shots']; entry['evaluations']+=audited['evaluations']
        if seen!=set(expected) or len(seen)!=manifest['reports']: raise ValueError('missing reports')
        for policy,entry in policies.items():
            old=summary['summaries'][policy]
            if entry['outcomes']!=old['outcomes'] or entry['cases']!=old['cases'] or entry['shots']!=old['total_shots'] or entry['evaluations']!=old['evaluations']:
                raise ValueError('aggregate mismatch')
    except (OSError,ValueError,KeyError,TypeError,EOFError) as exc:
        errors.append(type(exc).__name__+': '+str(exc))
    return {'valid':not errors,'errors':errors,'reports':len(seen),'policies':policies,
        'scope':'Historical recorded counts and unsigned bindings; no replay, authenticity or current-source holdout claim'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT/'benchmarks/historical-recovery-v1')
    args=parser.parse_args(); result=verify(args.root)
    print(json.dumps(result,indent=2));return 0 if result['valid'] else 1


if __name__=='__main__':raise SystemExit(main())
