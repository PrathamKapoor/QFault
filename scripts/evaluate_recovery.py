"""Separate selected recovery trials and rejection controls; no policy tuning."""
import argparse,json
from pathlib import Path
from qfault.workflow import RunRequest,investigate,scenario as make_scenario
from qfault.storage import ArtifactStore,verify_export
from qfault.quantum import benchmark,contract,Circuit,Gate,Noise
from qfault.recovery import IndependentVerifier
from qfault.diagnostics import ExecutionBudget
from qfault.experiments import event_rate
from qfault.evidence import canonical,digest

parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
out=Path(args.out)
out.mkdir(parents=True,exist_ok=False)
store=ArtifactStore(out/'investigations')
rows=[]
for family,n,scenario in [('bell',2,'remove'),('ghz',4,'remove'),('bell',2,'phase'),('ghz',4,'phase'),('qft',2,'phase'),('qft',4,'phase')]:
    for seed in [503,509]:
        request=RunRequest(family=family,n_qubits=n,scenario=scenario,policy='phase',seed=seed,max_shots=20000,max_evaluations=600)
        _,submitted,_,_=make_scenario(request)
        submitted_digest=digest(submitted.model_dump(mode='json'))
        result=investigate(request)
        eid=store.save(result)
        proposal=result['recovery']
        verdict=(proposal or {}).get('verification',{})
        rows.append({'family':family,'n_qubits':n,'scenario':scenario,'seed':seed,'experiment_id':eid,
            'diagnosis':result['diagnosis']['category'],'status':(proposal or {}).get('status','NO_PROPOSAL'),
            'verified':verdict.get('verified_status')=='VERIFIED','shots':result['cost']['shots'],
            'evaluations':result['cost']['evaluations'],'original_Z_quality':verdict.get('original_quality'),
            'candidate_Z_quality':verdict.get('candidate_quality'),'original_phase_quality':verdict.get('original_phase_quality'),
            'candidate_phase_quality':verdict.get('candidate_phase_quality'),
            'original_preserved':digest(result['candidate'])==submitted_digest,
            'export_valid':verify_export(store.export(eid))['valid'],'artifact_path':str(out/'investigations'/eid)})
controls=[]
good=benchmark('bell',2)
phase=Circuit(n_qubits=2,gates=good.gates+(Gate(name='z',qubits=(0,)),))
for name,c,noise in [('invalid_phase_counts_match',phase,Noise()),('systematically_noisy_correct_state',good,Noise(readout=.3))]:
    budget=ExecutionBudget(4096,3)
    result=IndependentVerifier().verify(c,contract('bell',2),noise,2048,9001,budget,phase_validate=True)
    (out/(name+'.json')).write_bytes(canonical(result))
    controls.append({'name':name,'status':result['verified_status'],'state_fidelity':result['state_fidelity'],
        'Z_comparison':result['distribution_comparison'],'phase_comparison':result['phase_distribution_comparison'],
        'shots':budget.shots,'evaluations':budget.evaluations,'artifact_path':str(out/(name+'.json')),'artifact_digest':digest(result)})
summary={'rows':rows,'controls':controls,'verified':event_rate(sum(r['verified'] for r in rows),len(rows)),
    'limitations':['Selected fixed templates and two seeds; not a general repair success rate','One-edit search capped at 256; no evaluator mutation parameters enter planner',
        'Independent implementation and fresh measurements share Qiskit; not independent-vendor unitary equivalence']}
(out/'summary.json').write_bytes(canonical(summary))
print(json.dumps(summary,indent=2))
