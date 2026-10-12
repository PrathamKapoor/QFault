"""One-shot execution of the committed measurement-boundary protocol.

All configured cases, including failed executions, remain in the output.
Output directories are exclusive; this runner never edits frozen benchmarks.
"""
import argparse
import hashlib
import json
import platform
import subprocess
from pathlib import Path
from time import perf_counter
from importlib.metadata import version
from qfault.workflow import RunRequest,scenario,investigate
from qfault.quantum import Circuit,Noise
from qfault.experiments import evaluator_truth
from qfault.evidence import canonical,digest
from qfault.storage import ArtifactStore


def cases(protocol):
    for family,n in protocol['circuits']:
        conditions=protocol['conditions']+(protocol['qft_extra'] if family=='qft' else [])
        for condition in conditions:
            for seed in protocol['seeds']:
                yield dict(case_id=f"{family}{n}/{condition['name']}/{seed}",family=family,
                           n_qubits=n,seed=seed,condition=condition)


def rate(k,n):
    return dict(successes=k,n=n,rate=k/n if n else None)


def summarize(rows):
    confusion={}
    for r in rows:
        matrix=confusion.setdefault(r['truth'],{})
        matrix[r['prediction']]=matrix.get(r['prediction'],0)+1
    clean=[r for r in rows if r['truth']=='NO_SIGNIFICANT_FAILURE_DETECTED']
    selected=[r for r in rows if not r['abstained']]
    return dict(cases=len(rows),strict_attribution=rate(sum(r['strict_correct'] for r in rows),len(rows)),
        selective_accuracy=rate(sum(r['strict_correct'] for r in selected),len(selected)),
        abstention=rate(sum(r['abstained'] for r in rows),len(rows)),
        clean_false_diagnosis=rate(sum(not r['abstained'] and r['prediction']!='NO_SIGNIFICANT_FAILURE_DETECTED' for r in clean),len(clean)),
        supported_discrepancy=rate(sum(r['supported_discrepancy'] for r in rows),len(rows)),
        per_class_recall={truth:rate(sum(r['strict_correct'] for r in rows if r['truth']==truth),sum(r['truth']==truth for r in rows)) for truth in confusion},
        confusion_matrix=confusion,
        **{key:sum(r[key] for r in rows) for key in ['shots','additional_shots','evaluations','executions','runtime_seconds']},
        all_failure_cases=[r['case_id'] for r in rows if not r['strict_correct']])


def prepared(request,condition):
    original,candidate,noise,truth=scenario(request)
    noise=Noise(readout=condition.get('readout',noise.readout),depolarizing=condition.get('depolarizing',noise.depolarizing))
    truth['noise']=noise.model_dump()
    if 'angle_delta' in condition:
        index=truth['mutation']['index']
        gates=list(original.gates)
        gates[index]=gates[index].model_copy(update={'angle':gates[index].angle+condition['angle_delta']})
        candidate=Circuit(n_qubits=original.n_qubits,gates=tuple(gates))
        truth['mutation']['angle_delta']=condition['angle_delta']
        truth['mutation']['result_digest']=digest(candidate.model_dump(mode='json'))
    return original,candidate,noise,truth


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True)
    parser.add_argument('--protocol',default='benchmarks/measurement-holdout-protocol.json')
    args=parser.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
    protocol=json.loads(Path(args.protocol).read_bytes());(out/'protocol.json').write_bytes(canonical(protocol))
    # Provenance is recorded before any evaluation, including the implementation bytes.
    implementation={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [*Path('qfault').glob('*.py'),Path(__file__)]}
    commit=subprocess.check_output(['git','-c','safe.directory=C:/Projects/QFF','rev-parse','HEAD'],text=True).strip()
    provenance=dict(commit=commit,protocol_digest=digest(protocol),implementation=implementation,
        python=platform.python_version(),packages={p:version(p) for p in ['qiskit','qiskit-aer','numpy','scipy']})
    (out/'provenance.json').write_bytes(canonical(provenance))
    store=ArtifactStore(out/'investigations');rows=[];start=perf_counter()
    with (out/'rows.jsonl').open('x',encoding='utf8') as stream:
        for policy in protocol['policies']:
            for case in cases(protocol):
                measurement=policy.startswith('measurement_')
                request=RunRequest(family=case['family'],n_qubits=case['n_qubits'],scenario=case['condition']['scenario'],
                    seed=case['seed'],shots=protocol['shots'],max_shots=protocol['max_shots'],
                    max_evaluations=protocol['max_evaluations'],backend=protocol['backend'],recover=False,
                    diagnostic_mode='measurement_only' if measurement else 'simulator_assisted',
                    measurement_plan='z_only' if policy=='measurement_z' else 'complementary',
                    policy='fixed' if policy=='simulator_fixed' else 'phase')
                setup=prepared(request,case['condition'])
                base={k:v for k,v in case.items() if k!='condition'}|{'condition':case['condition']['name'],'policy':policy}
                try:
                    result=investigate(request,prepared=setup)
                    assert result['prediction_digest']==digest({'diagnosis':result['diagnosis'],'recovery':result['recovery']})
                    truth,infidelity=evaluator_truth(result)  # evaluator invoked after prediction freeze
                    prediction=result['diagnosis']['category']
                    abstained=prediction in protocol['measurement_abstentions' if measurement else 'simulator_abstentions']
                    cost=result['cost'];eid=store.save(result);assert store.verify(eid)['valid']
                    phase=result['diagnosis'].get('phase_probe')
                    supported=result['diagnosis']['discrepancy']['significant_disagreement'] or bool(phase and phase['comparison']['significant_disagreement'])
                    row=base|dict(truth=truth,evaluator_infidelity=infidelity,prediction=prediction,abstained=abstained,
                        strict_correct=prediction==truth and not abstained,supported_discrepancy=supported,
                        shots=cost['shots'],additional_shots=cost['shots']-2*protocol['shots'],evaluations=cost['evaluations'],
                        executions=cost['circuit_executions'],runtime_seconds=cost['runtime_seconds'],
                        exact_state_evaluations=cost['exact_state_evaluations'],prediction_digest=result['prediction_digest'],
                        experiment_id=eid,artifact_path=str(store.folder(eid)),manifest_sha256=hashlib.sha256((store.folder(eid)/'manifest.json').read_bytes()).hexdigest())
                except Exception as exc:
                    # Keep the failed case and continue; no replacement seeds.
                    row=base|dict(truth='EXECUTION_ERROR',prediction='UNSUPPORTED',abstained=True,strict_correct=False,
                        supported_discrepancy=False,shots=0,additional_shots=0,evaluations=0,executions=0,
                        runtime_seconds=0,error=type(exc).__name__+': '+str(exc),cost_unknown=True)
                rows.append(row);stream.write(json.dumps(row)+'\n');stream.flush()
            print(policy+' completed',flush=True)
    pairs={}
    for a,b in [('measurement_z','measurement_complementary'),('measurement_complementary','simulator_phase'),('simulator_fixed','simulator_phase')]:
        left={r['case_id']:r for r in rows if r['policy']==a};right={r['case_id']:r for r in rows if r['policy']==b}
        pairs[a+' vs '+b]={key:sum((x['strict_correct'],right[c]['strict_correct'])==flags for c,x in left.items())
            for key,flags in [('both_correct',(True,True)),('left_only',(True,False)),('right_only',(False,True)),('neither',(False,False))]}
        pairs[a+' vs '+b]['right_minus_left_shots']=sum(right[c]['shots']-x['shots'] for c,x in left.items())
    summary=dict(protocol=protocol,provenance=provenance,policies={p:summarize([r for r in rows if r['policy']==p]) for p in protocol['policies']},
        paired_descriptive=pairs,execution_errors=[r for r in rows if 'error' in r],wall_seconds=perf_counter()-start,
        limits=protocol['limits']+[protocol['paired_analysis'],'No class-probability estimates or inferential p-values; configured noise may be unobservable'])
    (out/'results.json').write_bytes(canonical(summary|{'rows':rows}))
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
    print(json.dumps({'cases':len(rows),'errors':len(summary['execution_errors']),'wall_seconds':summary['wall_seconds']},indent=2))


if __name__=='__main__':main()
