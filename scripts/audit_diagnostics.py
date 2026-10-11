"""Post-prediction audit of previously observed evaluation; never diagnostic features."""
import json
from pathlib import Path
import numpy as np
from qfault.quantum import Circuit,Noise,contract,ideal_state,probabilities,noisy_density
from qfault.evidence import digest
from qfault.storage import ArtifactStore

source=Path('benchmarks/results.json')
summary=json.loads(source.read_bytes())
reproduction=json.loads(Path('artifacts/stabilization-original/summary.json').read_bytes())
rows=[]
for row in summary['rows']:
    folder=Path(row['artifact_path'])
    store=ArtifactStore(folder.parent)
    if not store.verify(row['experiment_id'])['valid']: raise ValueError('source artifact integrity failed')
    record=store.load(row['experiment_id'])
    circuit=Circuit.model_validate(record['candidate'])
    spec=contract(row['family'],circuit.n_qubits)
    state=ideal_state(circuit)
    expected=probabilities(spec.state())
    actual=probabilities(state)
    ideal_z_tv=.5*sum(abs(expected[k]-actual[k]) for k in expected)
    diagnosis=record['diagnosis']
    wrong=row['truth']!=row['prediction']
    calibration=diagnosis['readout_probe']
    if not wrong:
        cause='correct_category'
    elif calibration and calibration['significant_disagreement'] and row['prediction']=='NO_SIGNIFICANT_FAILURE_DETECTED':
        cause='collected_calibration_evidence_not_used_in_final_decision'
    elif row['evaluator_state_infidelity']>spec.state_infidelity_tolerance and diagnosis['state_probe'] is None:
        cause='Z_basis_cannot_distinguish_logical_state' if ideal_z_tv<1e-10 else 'logical_evidence_not_collected_after_weak_Z_disagreement'
    elif row['truth']=='NOISE_CONSISTENT_DEGRADATION':
        cause='noise_unobservable_or_underpowered_in_Z_basis'
    else:
        cause='policy_or_budget_did_not_resolve_hypotheses'
    rows.append({**row,'wrong':wrong,'audit_cause':cause,'ideal_Z_TV':ideal_z_tv,
        'discrepancy':diagnosis['discrepancy'],'state_probe_collected':diagnosis['state_probe'] is not None,
        'readout_probe':calibration,'hypotheses':diagnosis['hypotheses'],'actions':record['cost']['actions'],
        'remaining_shots':record['cost']['max_shots']-record['cost']['shots'],
        'remaining_evaluations':record['cost']['max_evaluations']-record['cost']['evaluations']})
counts={}
for r in rows:
    counts.setdefault(r['policy'],{})[r['audit_cause']]=counts.setdefault(r['policy'],{}).get(r['audit_cause'],0)+1
result={'source':str(source),'source_digest':digest(summary),
    'reproduction':'artifacts/stabilization-original','scientific_metrics_reproduced':summary['policies']==reproduction['policies'],
    'original_confusion_matrices':{p:m['confusion_matrix'] for p,m in summary['policies'].items()},
    'audit_counts':counts,'rows':rows,
    'limitations':['Audit uses evaluator truth after predictions; none of these features enter diagnosis',
                   'Cause labels distinguish demonstrable missing evidence/basis limits; weak evidence can have overlapping causes',
                   'No hypothesis scores were calibrated probabilities; original engine has support labels only']}
Path('benchmarks/policy-audit.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps({'reproduced':result['scientific_metrics_reproduced'],'causes':counts},indent=2))
