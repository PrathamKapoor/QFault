import numpy as np
import pytest
from qiskit.quantum_info import Statevector
from qfault import quantum
from qfault.workflow import investigate,RunRequest

@pytest.mark.parametrize('family,n',[('bell',2),('ghz',4),('qft',2),('qft',4)])
def test_relative_phase_hidden_in_z_is_visible_in_contract_basis(family,n):
    good=quantum.benchmark(family,n)
    bad=quantum.Circuit(n_qubits=n,gates=good.gates+(quantum.Gate(name='z',qubits=(0,)),))
    assert np.allclose(list(quantum.probabilities(quantum.ideal_state(good)).values()),list(quantum.probabilities(quantum.ideal_state(bad)).values()))
    assert hasattr(quantum,'measurement_rotation'), 'phase-sensitive contract measurement missing'
    spec=quantum.contract(family,n)
    rotation=quantum.measurement_rotation(spec)
    a=Statevector(quantum.ideal_state(good)).evolve(rotation.native()).probabilities()
    b=Statevector(quantum.ideal_state(bad)).evolve(rotation.native()).probabilities()
    assert .5*np.abs(a-b).sum()>.99
    global_phase=Statevector(np.exp(.37j)*quantum.ideal_state(good)).evolve(rotation.native()).probabilities()
    assert np.allclose(a,global_phase)

@pytest.mark.parametrize('family,n',[('bell',2),('ghz',4),('qft',4)])
def test_phase_policy_collects_actual_phase_counts_and_links_evidence(family,n):
    assert 'phase' in RunRequest.model_fields['policy'].annotation.__args__, 'phase policy missing'
    r=investigate(RunRequest(family=family,n_qubits=n,scenario='phase',policy='phase',recover=False,seed=71))
    assert r['diagnosis']['category']=='LOGICAL_CIRCUIT_DEFECT'
    p=r['diagnosis']['phase_probe']
    assert p['comparison']['significant_disagreement']
    assert p['execution_id'] in r['diagnosis']['evidence_references']
    record=next(e for e in r['executions'] if e['execution_id']==p['execution_id'])
    assert sum(record['output_counts'].values())==2048
    assert record['measurement_basis']==p['basis']
    assert r['cost']['shots']==sum(e['executed_shots'] for e in r['executions'])


def test_phase_policy_abstains_without_complementary_measurement_budget():
    assert 'phase' in RunRequest.model_fields['policy'].annotation.__args__, 'phase policy missing'
    r=investigate(RunRequest(scenario='phase',policy='phase',max_shots=4096,max_evaluations=2,recover=False))
    assert r['diagnosis']['category']=='INSUFFICIENT_EVIDENCE'
    assert r['cost']['shots']==4096


def test_phase_recovery_has_fresh_phase_validation():
    assert 'phase' in RunRequest.model_fields['policy'].annotation.__args__, 'phase policy missing'
    r=investigate(RunRequest(scenario='phase',policy='phase',seed=71))
    v=r['recovery']['verification']
    assert v['verified_status']=='VERIFIED'
    assert v['phase_execution']['seed']!=next(e for e in r['executions'] if e['execution_id']==r['diagnosis']['phase_probe']['execution_id'])['seed']
    assert r['cost']['shots']==sum(e['executed_shots'] for e in r['executions'])


def test_global_phase_operation_is_not_logical_defect():
    from qfault.diagnostics import DiagnosticAnalyst,DiagnosticAccess,ExecutionBudget,EvidenceCollector
    good=quantum.benchmark('bell',2)
    same=quantum.Circuit(n_qubits=2,gates=good.gates+(quantum.Gate(name='rz',qubits=(0,),angle=2*np.pi),))
    measured=EvidenceCollector.collect(quantum.execute(same,quantum.Noise(),2048,71),2)
    diagnosis=DiagnosticAnalyst().analyze(same,quantum.contract('bell',2),measured,DiagnosticAccess(same,quantum.Noise(),ExecutionBudget(8192,6),71),'phase')
    assert diagnosis['category']=='NO_SIGNIFICANT_FAILURE_DETECTED'


def test_phase_verification_rejects_attractive_counts_only_repair():
    from qfault.diagnostics import ExecutionBudget
    from qfault.recovery import IndependentVerifier
    good=quantum.benchmark('bell',2)
    bad=quantum.Circuit(n_qubits=2,gates=good.gates+(quantum.Gate(name='z',qubits=(0,)),))
    result=IndependentVerifier().verify(bad,quantum.contract('bell',2),quantum.Noise(),2048,101,ExecutionBudget(4096,3),phase_validate=True)
    assert result['distribution_comparison']['upper']<.1
    assert result['phase_distribution_comparison']['significant_disagreement']
    assert result['verified_status']=='REJECTED'


def test_phase_planner_preserves_validation_budget():
    from qfault.diagnostics import ExecutionBudget
    from qfault.recovery import RecoveryPlanner
    good=quantum.benchmark('bell',2)
    bad,_=quantum.mutate(good,'remove',1,71)
    budget=ExecutionBudget(4096,4)
    assert 'reserved_validation_shots' in __import__('inspect').signature(RecoveryPlanner.propose).parameters
    answer=RecoveryPlanner().propose(bad,quantum.contract('bell',2),budget,reserved_validation_shots=4096,reserved_validation_evaluations=3)
    assert budget.shots==0 and budget.evaluations<=1
    assert answer['status']!='PROPOSED'


def test_default_uses_strong_fixed_baseline():
    assert RunRequest().policy=='fixed'
