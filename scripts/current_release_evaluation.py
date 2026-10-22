"""Versioned current-source replication; never relabel observed data untouched."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

from qfault.counterfactual import RecoveryRequest,recover
from qfault.lab import LabRequest,investigate_lab
from qfault.storage import ArtifactStore,verify_export
from qfault.evidence import canonical,digest
from scripts.replicate_external_subset import source_reports,projection
from scripts.audit_counterfactual import audit_record

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/'configs/current-release-replication-v4.json'
SOURCES=sorted([p.relative_to(ROOT).as_posix() for p in (ROOT/'qfault').glob('*.py')]+[
    'scripts/current_release_evaluation.py','scripts/replicate_external_subset.py',
    'scripts/audit_counterfactual.py','requirements.lock','pyproject.toml'])
OLD_NOTE='No recovery class is validated for custom-circuit contracts (including target states); repair selection from measurements is not implemented.'
NEW_NOTE='Automatic recovery is not part of an ordinary laboratory investigation. Use the separate bounded measured-recovery operation to screen edits and collect fresh verification.'


def git(*args):
    return subprocess.check_output(['git','-c','safe.directory='+ROOT.as_posix(),*args],cwd=ROOT,text=True).strip()


def hashes():
    return {name:hashlib.sha256((ROOT/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest() for name in SOURCES}


def normalized(record):
    value=projection(record)
    if value.get('investigation_kind')=='custom_circuit':
        if value['recovery']['reason'] not in (OLD_NOTE,NEW_NOTE):
            raise ValueError('Unexpected ordinary-lab explanation change')
        value['recovery']['reason']='ORDINARY_LAB_NO_AUTOMATIC_RECOVERY'
    return value


def freeze():
    old=json.loads((ROOT/'configs/final-verification-subset-v1.json').read_bytes())
    reports=source_reports(); cases=[]
    for case in old['cases']:
        record=reports[case['case_key']]['investigation']
        cases.append({'case_key':case['case_key'],'mode':case['mode'],'request':case['request'],
            'request_sha256':digest(case['request']),
            'expected_projection_sha256':digest(normalized(record))})
    data={'schema_version':1,'name':PROTOCOL.stem,
        'study_type':'deterministic replication of observed cases; NOT an untouched holdout or new performance study',
        'source_hash_rule':'SHA256 after replacing each CRLF byte pair with LF; otherwise preserve UTF-8 bytes exactly. Separate from historical byte digests.',
        'source_sha256_normalized_lf':hashes(),'cases':cases,
        'selection':'Exact prior 72-case outcome-independent subset; no new outcome-based selection',
        'accepted_metadata_delta':'Only the explicitly enumerated ordinary-lab recovery explanation; all scientific fields retained',
        'acceptance':'72 new valid exports, exact normalized scientific projections, no errors; independent count-based recovery reconstruction',
        'archive_sha256':hashlib.sha256((ROOT/'benchmarks/external-holdout-v1/reports.jsonl.gz').read_bytes()).hexdigest()}
    with PROTOCOL.open('xb') as stream:stream.write(canonical(data))
    print('Frozen protocol; commit source and protocol before --run')


def run(out):
    data=json.loads(PROTOCOL.read_bytes())
    if data['schema_version']!=1 or data['source_sha256_normalized_lf']!=hashes():
        raise ValueError('Current release sources differ from frozen protocol')
    registered=SOURCES+[PROTOCOL.relative_to(ROOT).as_posix()]
    if set(git('ls-files','--',*registered).splitlines())!=set(registered) or git('diff','HEAD','--',*registered):
        raise ValueError('Commit protocol and sources before execution')
    archive_path=ROOT/'benchmarks/external-holdout-v1/reports.jsonl.gz'
    if hashlib.sha256(archive_path.read_bytes()).hexdigest()!=data['archive_sha256']:
        raise ValueError('Original archive changed')
    out=Path(out).resolve()
    if not out.is_relative_to((ROOT/'artifacts').resolve()):raise ValueError('output must be inside artifacts')
    out.mkdir(parents=True,exist_ok=False);store=ArtifactStore(out/'investigations');rows=[]
    with gzip.open(out/'reports.jsonl.gz','wb') as archive:
        for case in data['cases']:
            row={'case_key':case['case_key'],'mode':case['mode']}
            try:
                request=case['request']
                if digest(request)!=case['request_sha256']:raise ValueError('request digest mismatch')
                result=recover(RecoveryRequest.model_validate(request)) if case['mode']=='recovery' else investigate_lab(LabRequest.model_validate(request))
                eid=store.save(result);report=store.export(eid)
                if not verify_export(report)['valid']:raise ValueError('export verification failed')
                if case['mode']=='recovery':audit_record(report['investigation'])
                matched=digest(normalized(report['investigation']))==case['expected_projection_sha256']
                row.update(experiment_id=eid,matched=matched,export_valid=True,
                    shots=result['cost']['shots'],evaluations=result['cost']['evaluations'],
                    status=result.get('status',result['diagnosis']['category']))
                archive.write(canonical(report)+b'\n')
            except Exception as exc:row.update(matched=False,error=type(exc).__name__+': '+str(exc))
            rows.append(row)
            print(json.dumps({'completed':len(rows),'matched':row['matched'],'error':row.get('error')}),flush=True)
    summary={'schema_version':1,'protocol':data['name'],'protocol_sha256':hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        'source_commit':git('rev-parse','HEAD'),'source_sha256_normalized_lf':hashes(),'rows':rows,
        'runs':len(rows),'matched':sum(r['matched'] for r in rows),'errors':sum('error' in r for r in rows),
        'shots':sum(r.get('shots',0) for r in rows),'evaluations':sum(r.get('evaluations',0) for r in rows),
        'outcomes':dict(Counter(r.get('status','ERROR') for r in rows)),
        'reports_sha256':hashlib.sha256((out/'reports.jsonl.gz').read_bytes()).hexdigest(),
        'scope':data['study_type']}
    summary['passed']=summary['runs']==72 and summary['matched']==72 and summary['errors']==0
    (out/'summary.json').write_bytes(canonical(summary))
    print(json.dumps({k:v for k,v in summary.items() if k not in ('rows','source_sha256_normalized_lf')},indent=2))
    return 0 if summary['passed'] else 1


def main():
    global PROTOCOL
    parser=argparse.ArgumentParser(description=__doc__)
    action=parser.add_mutually_exclusive_group(required=True);action.add_argument('--freeze',action='store_true');action.add_argument('--run',action='store_true')
    parser.add_argument('--out',default='artifacts/current-release-replication-v4')
    parser.add_argument('--protocol',default=str(PROTOCOL))
    args=parser.parse_args()
    PROTOCOL=Path(args.protocol).resolve()
    if args.freeze:freeze();return 0
    return run(args.out)


if __name__=='__main__':raise SystemExit(main())
