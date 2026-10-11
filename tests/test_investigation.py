import copy
import pytest
from pydantic import ValidationError
from qfault.quantum import benchmark,contract,mutate,Noise,Circuit,Gate,execute
from qfault.diagnostics import EvidenceCollector,DiagnosticAnalyst,ExecutionBudget,DiagnosticAccess
from qfault.recovery import RecoveryPlanner,IndependentVerifier
from qfault.workflow import investigate,RunRequest,Supervisor


def test_clean_no_false_logical_diagnosis():
    r=investigate(RunRequest(family="bell",scenario="clean",shots=2048,seed=3))
    assert r["diagnosis"]["category"]=="NO_SIGNIFICANT_FAILURE_DETECTED"
    assert r["recovery"] is None


def test_readout_does_not_become_logical_defect():
    r=investigate(RunRequest(family="bell",scenario="readout",shots=2048,seed=3))
    assert r["diagnosis"]["category"]=="NOISE_CONSISTENT_DEGRADATION"
    assert r["recovery"] is None


def test_fault_repair_independently_checked():
    r=investigate(RunRequest(family="bell",scenario="remove",shots=2048,seed=3))
    assert r["diagnosis"]["category"]=="LOGICAL_CIRCUIT_DEFECT"
    assert r["recovery"]["verification"]["verified_status"]=="VERIFIED"
    assert r["recovery"]["edit"]["edit_count"]==1
    assert r["recovery"]["verification"]["validation_seed"]!=3
    assert r["candidate"]["gates"]!=r["recovery"]["candidate"]["gates"]


def test_mixed_fault_is_not_asserted_as_pure_logical():
    r=investigate(RunRequest(family="bell",scenario="mixed",shots=2048,seed=3))
    assert r["diagnosis"]["category"]=="MIXED_OR_AMBIGUOUS"


def test_exhausted_budget_abstains():
    r=investigate(RunRequest(family="bell",scenario="remove",shots=1024,max_shots=2048,max_evaluations=2))
    assert r["diagnosis"]["category"]=="INSUFFICIENT_EVIDENCE"
    assert r["cost"]["shots"]<=2048 and r["cost"]["evaluations"]<=2


def test_evaluator_truth_is_not_an_analyst_input():
    c=benchmark("bell",2)
    record=execute(c,Noise(),1024,1)
    one=EvidenceCollector.collect(record,2)
    poisoned=copy.deepcopy(record)
    poisoned["ground_truth"]={"operator":"remove","index":999}
    poisoned["noise_configuration"]={"readout":1}
    two=EvidenceCollector.collect(poisoned,2)
    assert one==two
    with pytest.raises(ValidationError): type(one)(**one.model_dump(),ground_truth="remove")
    # Analyst receives the same immutable projection and bounded oracle in both runs.
    a=DiagnosticAnalyst().analyze(c,contract("bell",2),one,DiagnosticAccess(c,Noise(),ExecutionBudget(10000,100),9),"evidence")
    b=DiagnosticAnalyst().analyze(c,contract("bell",2),two,DiagnosticAccess(c,Noise(),ExecutionBudget(10000,100),9),"evidence")
    assert a==b


def test_invalid_repair_rejected():
    good=benchmark("bell",2)
    bad,_=mutate(good,"remove",1,2)
    v=IndependentVerifier().verify(bad,contract("bell",2),Noise(),2048,91,ExecutionBudget(10000,10))
    assert v["verified_status"]=="REJECTED"
    assert not v["contract_satisfied"]


def test_phase_fault_is_detected_only_by_state_diagnostic():
    c=benchmark("bell",2)
    phase=Circuit(n_qubits=2,gates=c.gates+(Gate(name="z",qubits=(0,)),))
    m=EvidenceCollector.collect(execute(phase,Noise(),2048,7),2)
    d=DiagnosticAnalyst().analyze(phase,contract("bell",2),m,DiagnosticAccess(phase,Noise(),ExecutionBudget(10000,100),7),"evidence")
    assert d["category"]=="NO_SIGNIFICANT_FAILURE_DETECTED"
    assert d["state_infidelity"] is None
    # Measurement-triggered policy cannot see this fault; fixed plan can.
    d=DiagnosticAnalyst().analyze(phase,contract("bell",2),m,DiagnosticAccess(phase,Noise(),ExecutionBudget(10000,100),7),"fixed")
    assert d["category"]=="LOGICAL_CIRCUIT_DEFECT"


def test_budget_cannot_overrun():
    b=ExecutionBudget(100,1)
    b.reserve(100,"first")
    with pytest.raises(ValueError): b.reserve(1,"second")
    assert b.shots==100 and b.evaluations==1


def test_state_machine_rejects_skips():
    s=Supervisor()
    with pytest.raises(ValueError): s.transition("VERIFIED")


def test_corrupt_counts_not_healthy():
    with pytest.raises(ValueError): EvidenceCollector.collect({"output_counts":{"00":3},"executed_shots":4,"execution_id":"e","execution_status":"SUCCEEDED"},2)


def test_observation_provenance_and_actual_shot_cost():
    r=investigate(RunRequest(scenario="remove",seed=7))
    ids={e["execution_id"] for e in r["executions"]}
    assert r["cost"]["circuit_executions"]==len(r["executions"])
    assert r["cost"]["shots"]==sum(e["executed_shots"] for e in r["executions"])
    assert all(set(o["evidence_references"])<=ids for o in r["observations"])
    assert {o["kind"] for o in r["observations"]} >= {"measured","derived"}


def test_inconclusive_recovery_never_has_success_state():
    r=investigate(RunRequest(scenario="remove",max_evaluations=26,seed=42))
    assert r["recovery"]["verification"]["verified_status"]=="INCONCLUSIVE"
    assert "VERIFIED" not in {s["state"] for s in r["supervisor"]["history"]}
