"""Preregister and rerun a bounded frozen subset without changing original evidence.

Freeze exact requests first, commit this script and its protocol, then run. Selection
uses sorted source paths and fixed index arithmetic, never outcomes or exact truth.
This checks deterministic reproduction; reused seeds are not independent evidence.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
from time import perf_counter

from qfault.counterfactual import RecoveryRequest, recover
from qfault.evidence import digest
from qfault.lab import LabRequest, investigate_lab
from qfault.storage import ArtifactStore, verify_export

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / 'configs/final-verification-subset-v1.json'
ARCHIVE = ROOT / 'benchmarks/external-holdout-v1/reports.jsonl.gz'
SCRIPT = 'scripts/replicate_external_subset.py'
SOURCES = [SCRIPT, 'qfault/lab.py', 'qfault/target.py', 'qfault/counterfactual.py',
           'qfault/recovery_observation.py', 'qfault/interventions.py', 'qfault/quantum.py',
           'qfault/backends.py', 'qfault/diagnostics.py', 'qfault/evidence.py', 'qfault/storage.py']
KINDS = ['measurement_distribution', 'pauli_expectations', 'target_state']
VARIANTS = ['clean', 'remove_first', 'readout']
POLICIES = ['fixed', 'adaptive', 'adaptive_witness']
VOLATILE = {'experiment_id', 'execution_id', 'created_at', 'runtime_seconds',
            'screening_digest', 'prediction_digest', 'digest', 'software_versions',
            'evaluation_truth', 'human_decisions'}


def git(*args):
    return subprocess.check_output(['git', '-c', 'safe.directory='+ROOT.as_posix(), *args],
                                   cwd=ROOT, text=True).strip()


def source_hashes():
    return {p: hashlib.sha256((ROOT/p).read_bytes().replace(b'\r\n', b'\n')).hexdigest()
            for p in SOURCES}


def projection(value):
    """Keep decisions, claims, all counts/seeds, candidate identities and resource cost.

    Remove instance IDs, clocks, runtime, software labels and digests that include
    those instance fields. Structural circuit/contract IDs and input digests remain.
    """
    if isinstance(value, dict):
        return {k: projection(v) for k,v in value.items() if k not in VOLATILE}
    if isinstance(value, list): return [projection(x) for x in value]
    # Pydantic defaults can serialize a declared zero as0 versus0.0 after replay.
    # They are the same scientific quantity; normalize only exact integer values.
    if isinstance(value,float) and value.is_integer(): return int(value)
    return value


def case_key(report):
    r=report['investigation']; cfg=r['configuration']; e=report['evaluation']
    mode='recovery' if r['investigation_kind']=='counterfactual_recovery' else 'diagnostic'
    return '|'.join(map(str, [mode,e['source_path'],cfg['contract']['kind'],e['variant'],
                             cfg.get('selection_policy',cfg.get('policy')),cfg['seed']]))


def source_reports():
    reports={}
    with gzip.open(ARCHIVE,'rt',encoding='utf-8') as stream:
        for line in stream:
            report=json.loads(line); key=case_key(report)
            if key in reports: raise ValueError('duplicate source case: '+key)
            reports[key]=report
    return reports


def selected_keys(reports):
    paths=sorted({r['evaluation']['source_path'] for r in reports.values()})
    if len(paths)!=9: raise ValueError('Expected exactly nine holdout programs')
    keys=[]
    for i,path in enumerate(paths):
        for j,kind in enumerate(KINDS):
            for k,variant in enumerate(VARIANTS):
                if k==(i+j)%3: continue
                keys.append('|'.join(map(str,['diagnostic',path,kind,variant,POLICIES[j],91001])))
        for policy in ('conservative','point_discrepancy'):
            keys.append('|'.join(map(str,['recovery',path,'pauli_expectations','remove_first',policy,91001])))
    if len(keys)!=72 or any(key not in reports for key in keys):
        raise ValueError('Prespecified selection does not match source archive')
    return keys


def freeze():
    reports=source_reports(); keys=selected_keys(reports)
    protocol={'name':'final-verification-subset-v1','base_revision':git('rev-parse','HEAD'),
        'archive_path':ARCHIVE.relative_to(ROOT).as_posix(),
        'archive_sha256':hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
        'selection':'Sorted nine source paths i; contract order distribution/Pauli/target j; variant order clean/remove_first/readout k. Include k != (i+j)%3. Diagnostic policies fixed/adaptive/adaptive_witness respectively. Add each path remove_first recovery under conservative and point_discrepancy. All seed 91001. No outcome-dependent selection.',
        'run_count':72,'diagnostic_count':54,'recovery_count':18,
        'balance':'Every program has six diagnostics and two recoveries. Each contract has six clean, six first-gate-deletion and six readout diagnostics. Deletions are interventions; they need not violate a fixed-input contract.',
        'purpose':'Exact deterministic request replication, not independent performance or population evidence. Original counts/claims/statuses/costs are the comparator; UUID/time/runtime/software-label fields are excluded.',
        'acceptance':'Every new export verifies. All72 source requests and scientific projections match. Divergences and errors are retained without retuning or replacing requests. Nonzero process exit on any divergence/error.',
        'source_sha256_normalized_lf':source_hashes(),'cases':[]}
    for key in keys:
        old=reports[key]; request=old['investigation']['configuration']
        protocol['cases'].append({'case_key':key,'mode':key.split('|',1)[0],
            'source_experiment_id':old['investigation']['experiment_id'],
            'request':request,'request_sha256':digest(request),
            'expected_scientific_projection_sha256':digest(projection(old['investigation']))})
    with PROTOCOL.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(protocol,stream,indent=2,sort_keys=True,ensure_ascii=False);stream.write('\n')
    print(json.dumps({'protocol':str(PROTOCOL),'run_count':len(keys),'protocol_sha256':hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
                      'next':'Commit script and protocol before running any replication'},indent=2))


def differences(a,b,path='',limit=20):
    if type(a)!=type(b) and not (isinstance(a,(int,float)) and isinstance(b,(int,float))):
        return [{'path':path,'expected':a,'actual':b}]
    if isinstance(a,dict):
        out=[]
        for k in sorted(set(a)|set(b)):
            if k not in a or k not in b: out.append({'path':path+'/'+k,'missing':'expected' if k not in a else 'actual'})
            else: out.extend(differences(a[k],b[k],path+'/'+k,limit))
            if len(out)>=limit: break
        return out[:limit]
    if isinstance(a,list):
        if len(a)!=len(b): return [{'path':path,'expected_length':len(a),'actual_length':len(b)}]
        out=[]
        for i,(x,y) in enumerate(zip(a,b)):
            out.extend(differences(x,y,path+'/'+str(i),limit))
            if len(out)>=limit: break
        return out[:limit]
    return [] if a==b else [{'path':path,'expected':a,'actual':b}]


def run(out):
    start=perf_counter(); protocol=json.loads(PROTOCOL.read_text(encoding='utf-8'))
    if source_hashes()!=protocol['source_sha256_normalized_lf']: raise ValueError('Preregistered sources changed')
    if hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()!=protocol['archive_sha256']: raise ValueError('Frozen source archive changed')
    registered=SOURCES+[PROTOCOL.relative_to(ROOT).as_posix()]
    if set(git('ls-files','--',*registered).splitlines())!=set(registered): raise ValueError('Commit script and protocol before execution')
    if git('diff','HEAD','--',*registered): raise ValueError('Preregistered source/protocol edits are uncommitted')
    reports=source_reports()
    if [c['case_key'] for c in protocol['cases']]!=selected_keys(reports): raise ValueError('Selection changed')
    out=Path(out).resolve()
    # Restrict writes to this reviewer's explicitly assigned artifact area.
    owner=(ROOT/'.local/final-gate/replication').resolve()
    if out!=owner and owner not in out.parents: raise ValueError('Output must be inside .local/final-gate/replication')
    out.mkdir(parents=True,exist_ok=False); store=ArtifactStore(out/'investigations'); rows=[]
    with gzip.open(out/'reports.jsonl.gz','xt',encoding='utf-8') as archive, (out/'progress.jsonl').open('x',encoding='utf-8') as progress:
        for number,case in enumerate(protocol['cases'],1):
            row={'number':number,'case_key':case['case_key'],'mode':case['mode'],'source_experiment_id':case['source_experiment_id']}
            try:
                old=reports[case['case_key']]['investigation']; request=case['request']
                if digest(request)!=case['request_sha256'] or request!=old['configuration']: raise ValueError('Request differs from frozen source')
                old_projection=projection(old)
                if digest(old_projection)!=case['expected_scientific_projection_sha256']: raise ValueError('Expected source projection changed')
                # Only the exact request is passed into the engine. Source evaluation
                # metadata and comparator outcomes are never policy arguments.
                result=(recover(RecoveryRequest.model_validate(request)) if case['mode']=='recovery'
                        else investigate_lab(LabRequest.model_validate(request)))
                eid=store.save(result); exported=store.export(eid); verified=verify_export(exported)
                if not verified['valid']: raise ValueError('New export fails integrity: '+str(verified['errors']))
                new_projection=projection(exported['investigation']); diff=differences(old_projection,new_projection)
                row.update(experiment_id=eid,export_valid=True,matched=not diff,
                    differences=diff,expected_scientific_projection_sha256=case['expected_scientific_projection_sha256'],
                    actual_scientific_projection_sha256=digest(new_projection),
                    status=result.get('status',result['diagnosis']['category']),
                    shots=result['cost']['shots'],evaluations=result['cost']['evaluations'])
                archive.write(json.dumps(exported,separators=(',',':'))+'\n');archive.flush()
            except Exception as exc:
                row.update(matched=False,error=type(exc).__name__+': '+str(exc))
            rows.append(row); progress.write(json.dumps(row,separators=(',',':'))+'\n');progress.flush()
            print(json.dumps({'completed':number,'total':len(protocol['cases']),'case_key':case['case_key'],
                              'matched':row['matched'],'error':row.get('error')},separators=(',',':')),flush=True)
    summary={'protocol':PROTOCOL.relative_to(ROOT).as_posix(),'protocol_sha256':hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        'execution_revision':git('rev-parse','HEAD'),'source_sha256_normalized_lf':source_hashes(),
        'runs':len(rows),'matched':sum(r['matched'] for r in rows),'errors':sum('error' in r for r in rows),
        'divergences':sum(not r['matched'] and 'error' not in r for r in rows),
        'export_verified':sum(r.get('export_valid',False) for r in rows),
        'total_shots':sum(r.get('shots',0) for r in rows),'total_backend_evaluations':sum(r.get('evaluations',0) for r in rows),
        'outcomes':{mode:dict(Counter(r.get('status','ERROR') for r in rows if r['mode']==mode)) for mode in ('diagnostic','recovery')},
        'runtime_seconds':perf_counter()-start,'rows':rows,
        'interpretation':'Reused-seed deterministic replication of72 preregistered configurations across9 external programs. Not72 backend jobs, independent programs or new performance evidence.'}
    summary['passed']=summary['runs']==72 and summary['matched']==72 and summary['export_verified']==72
    with (out/'summary.json').open('x',encoding='utf-8') as stream: json.dump(summary,stream,indent=2);stream.write('\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('rows','source_sha256_normalized_lf')},indent=2))
    return 0 if summary['passed'] else 1


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    action=parser.add_mutually_exclusive_group(required=True);action.add_argument('--freeze',action='store_true');action.add_argument('--run',action='store_true')
    parser.add_argument('--out',default='.local/final-gate/replication/run-v1')
    args=parser.parse_args()
    if args.freeze: freeze();return 0
    return run(args.out)


if __name__=='__main__': raise SystemExit(main())
