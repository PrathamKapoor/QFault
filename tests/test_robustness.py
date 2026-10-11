import json
import pytest
from pydantic import ValidationError
from qfault.quantum import Circuit,Gate,Noise,benchmark,mutate,contract,execute
from qfault.workflow import RunRequest,investigate
from qfault.recovery import IndependentVerifier
from qfault.diagnostics import ExecutionBudget,EvidenceCollector
from qfault.evidence import canonical,digest
from qfault.storage import ArtifactStore

@pytest.mark.parametrize("operator,index",[("remove",0),("replace",0),("rewire",1),("angle",3)])
def test_mutations_are_valid_and_seeded(operator,index):
    original=benchmark("qft",3)
    a,_=mutate(original,operator,index,91)
    b,_=mutate(original,operator,index,91)
    assert a==b
    assert a.native().num_qubits==3
    assert execute(a,Noise(),128,91)["executed_shots"]==128


def test_insufficient_shots_abstain():
    r=investigate(RunRequest(shots=16))
    assert r["diagnosis"]["category"]=="INSUFFICIENT_EVIDENCE"
    assert r["recovery"] is None


def test_noisy_repair_can_be_rejected_despite_ideal_correctness():
    verified=IndependentVerifier().verify(benchmark("bell",2),contract("bell",2),Noise(readout=.3),2048,99,ExecutionBudget(5000,5))
    assert verified["state_fidelity"]>1-1e-8
    assert verified["verified_status"]=="REJECTED"
    assert not verified["contract_satisfied"]


def test_canonical_unicode_and_nan():
    assert canonical({"b":2,"a":"λ"})==canonical({"a":"λ","b":2})
    assert digest({"value":1})!=digest({"value":2})
    with pytest.raises(ValueError): canonical({"bad":float("nan")})


def test_missing_artifact_is_integrity_failure(tmp_path):
    store=ArtifactStore(tmp_path)
    r=investigate(RunRequest(shots=256,recover=False))
    eid=store.save(r)
    (tmp_path/eid/"evaluation.json").unlink()  # test-owned temporary artifact
    assert not store.verify(eid)["valid"]


def test_optional_aer_not_required_for_real_gate_noise():
    r=execute(benchmark("bell",2),Noise(depolarizing=.1),128,0)
    assert r["backend_name"]=="qiskit.quantum_info.DensityMatrix/Kraus"
    assert r["backend_type"]=="local_simulator"

@pytest.mark.parametrize("kwargs",[{"family":"bell","n_qubits":3},{"scenario":"angle","family":"bell"},{"seed":-1},{"shots":2048,"max_shots":2048},{"scenario":"unknown"}])
def test_invalid_requests(kwargs):
    with pytest.raises(ValidationError): RunRequest(**kwargs)


def test_partial_execution_cannot_be_collected_as_success():
    with pytest.raises(ValueError):
        EvidenceCollector.collect({"execution_status":"FAILED","output_counts":{},"failure_reason":"simulator unavailable"},2)
