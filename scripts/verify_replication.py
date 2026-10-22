"""Verify retained current-release replication records without rerunning the engine."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import zlib

from qfault.evidence import digest
from qfault.storage import verify_export
from scripts.current_release_evaluation import normalized
from scripts.audit_counterfactual import audit_record

ROOT=Path(__file__).resolve().parents[1]


def verify(root):
    errors=[];seen=set();shots=evaluations=0
    try:
        root=Path(root);summary=json.loads((root/'summary.json').read_bytes())
        if summary.get('schema_version')!=1 or summary.get('protocol')!='current-release-replication-v4':
            raise ValueError('unsupported replication schema/protocol')
        raw=(ROOT/'configs/current-release-replication-v4.json').read_bytes()
        if hashlib.sha256(raw).hexdigest()!=summary['protocol_sha256']:raise ValueError('protocol digest mismatch')
        protocol=json.loads(raw);cases={c['case_key']:c for c in protocol['cases']}
        rows=summary['rows'];by_id={r['experiment_id']:r for r in rows}
        if len(rows)!=72 or len(by_id)!=72 or {r['case_key'] for r in rows}!=set(cases):
            raise ValueError('missing/duplicate case or report identity')
        archive=root/'reports.jsonl.gz'
        if archive.stat().st_size>32*1024*1024 or hashlib.sha256(archive.read_bytes()).hexdigest()!=summary['reports_sha256']:
            raise ValueError('replication archive size/digest mismatch')
        expanded=0
        with gzip.open(archive,'rb') as stream:
            while line:=stream.readline(16*1024*1024+1):
                expanded+=len(line)
                if len(line)>16*1024*1024 or expanded>256*1024*1024:raise ValueError('archive expansion limit')
                report=json.loads(line)
                if not verify_export(report)['valid']:raise ValueError('invalid export')
                record=report['investigation'];eid=record['experiment_id']
                if eid in seen or eid not in by_id:raise ValueError('duplicate/unmatched export')
                seen.add(eid);row=by_id[eid];case=cases[row['case_key']]
                if digest(case['request'])!=case['request_sha256'] or digest(normalized(record['configuration']))!=digest(normalized(case['request'])):
                    raise ValueError('request differs from frozen protocol')
                if digest(normalized(record))!=case['expected_projection_sha256']:raise ValueError('scientific projection differs')
                counted=sum(e['executed_shots'] for e in record['executions'])
                if any(sum(e['output_counts'].values())!=e['executed_shots'] for e in record['executions']):raise ValueError('counts/shot mismatch')
                if row['shots']!=counted or row['evaluations']!=len(record['executions']):raise ValueError('row cost mismatch')
                if row['mode']!=case['mode'] or row['status']!=record.get('status',record['diagnosis']['category']):raise ValueError('row verdict/mode mismatch')
                if case['mode']=='recovery':audit_record(record)
                shots+=counted;evaluations+=len(record['executions'])
        if len(seen)!=72 or shots!=summary['shots'] or evaluations!=summary['evaluations']:
            raise ValueError('aggregate/report membership mismatch')
        if summary['runs']!=72 or summary['matched']!=72 or summary['errors']!=0 or not all(r['matched'] for r in rows):
            raise ValueError('recorded summary differs from full successful reconstruction')
    except (OSError,ValueError,KeyError,TypeError,EOFError,zlib.error) as exc:
        errors.append(type(exc).__name__+': '+str(exc))
    return {'valid':not errors,'errors':errors,'reports':len(seen),'shots':shots,'evaluations':evaluations,
        'scope':'Deterministic replication of observed cases; unsigned consistency and independent recovery interval reconstruction, not new holdout performance'}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=ROOT/'benchmarks/current-release-replication-v4')
    args=parser.parse_args();result=verify(args.root);print(json.dumps(result,indent=2));return 0 if result['valid'] else 1


if __name__=='__main__':raise SystemExit(main())
