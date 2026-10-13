"""Custom circuit laboratory: validation, Qiskit-referenced measurement maths, planner, privilege boundary."""
import copy
import numpy as np
import pytest
from pydantic import ValidationError
from qiskit import QuantumCircuit
from qiskit.quantum_info import Pauli, Statevector
import qfault.lab as lab
from qfault.lab import (CustomCircuit, PauliContract, LabRequest, investigate_lab,
                        measurement_circuit, parity_expectation, plan)
from qfault.quantum import execute, Noise
from qfault.evidence import digest

CLUSTER = {"schema_version": 1, "name": "3q cluster", "n_qubits": 3,
           "input": {"kind": "computational_basis", "bitstring": "000"},
           "gates": [{"name": "h", "qubits": [q]} for q in range(3)] +
                    [{"name": "cz", "qubits": [0, 1]}, {"name": "cz", "qubits": [1, 2]}]}
STAB = {"kind": "pauli_expectations", "observables": [{"pauli": p, "expected": 1.0, "tolerance": 0.1} for p in ("XZI", "ZXZ", "IZX")]}
ZERO2 = {"kind": "computational_basis", "bitstring": "00"}


def circ(**kw):
    return CustomCircuit.model_validate({**copy.deepcopy(CLUSTER), **kw})


def req(circuit=None, contract=None, **kw):
    return LabRequest.model_validate({"circuit": circuit or CLUSTER, "contract": contract or STAB, **kw})


def gates(*pairs):
    return [{"name": n, "qubits": [q] if isinstance(q, int) else list(q)} for n, q in pairs]


# ---- circuit validation
@pytest.mark.parametrize("patch", [
    {"gates": [{"name": "foo", "qubits": [0]}]},
    {"gates": [{"name": "cx", "qubits": [0]}]},
    {"gates": [{"name": "cx", "qubits": [1, 1]}]},
    {"gates": [{"name": "h", "qubits": [7]}]},
    {"gates": [{"name": "rx", "qubits": [0], "angle": 1e9}]},
    {"gates": [{"name": "rx", "qubits": [0]}]},
    {"gates": [{"name": "h", "qubits": [0]}] * 33},
    {"n_qubits": 9},
    {"input": {"kind": "computational_basis", "bitstring": "00"}},
    {"input": {"kind": "statevector", "bitstring": "000"}},
    {"unknown_field": 1},
])
def test_invalid_circuits_rejected(patch):
    with pytest.raises(ValidationError):
        circ(**patch)


def test_circuit_identity_stable_and_name_independent():
    a, b = circ(), circ(name="renamed")
    assert a.circuit_id == b.circuit_id
    assert a.circuit_id != circ(input={"kind": "computational_basis", "bitstring": "001"}).circuit_id


def test_nan_angle_rejected():
    with pytest.raises(ValidationError):
        circ(gates=[{"name": "rx", "qubits": [0], "angle": float("nan")}])


# ---- contract validation
@pytest.mark.parametrize("contract", [
    {"kind": "measurement_distribution", "expected_probabilities": {"00": .6, "11": .6}, "tolerance": .1},
    {"kind": "measurement_distribution", "expected_probabilities": {"00": -.1, "11": 1.1}, "tolerance": .1},
    {"kind": "measurement_distribution", "expected_probabilities": {"0a": 1.0}, "tolerance": .1},
    {"kind": "pauli_expectations", "observables": [{"pauli": "XQ", "expected": 1, "tolerance": .1}]},
    {"kind": "pauli_expectations", "observables": [{"pauli": "XX", "expected": 1.5, "tolerance": .1}]},
    {"kind": "pauli_expectations", "observables": [{"pauli": "II", "expected": 1, "tolerance": .1}]},
    {"kind": "pauli_expectations", "observables": [{"pauli": "XX", "expected": 1, "tolerance": .1}] * 2},
    {"kind": "pauli_expectations", "environment": "noisy", "observables": [{"pauli": "XX", "expected": 1, "tolerance": .1}]},
    {"kind": "target_state", "amplitudes": []},
])
def test_invalid_contracts_rejected(contract):
    with pytest.raises(ValidationError):
        req(circuit={**CLUSTER, "n_qubits": 2, "input": ZERO2, "gates": []}, contract=contract)


def test_contradictory_claims_rejected():
    flat = {**CLUSTER, "n_qubits": 2, "input": ZERO2, "gates": []}
    anti = {"kind": "pauli_expectations", "observables": [{"pauli": "XI", "expected": 1, "tolerance": .05},
                                                          {"pauli": "ZI", "expected": 1, "tolerance": .05}]}
    with pytest.raises(ValidationError, match="contradictory"):
        req(flat, anti)
    triple = {"kind": "pauli_expectations", "observables": [{"pauli": "ZI", "expected": 1, "tolerance": .05},
              {"pauli": "IZ", "expected": 1, "tolerance": .05}, {"pauli": "ZZ", "expected": -1, "tolerance": .05}]}
    with pytest.raises(ValidationError, match="contradictory"):
        req(flat, triple)


def test_length_mismatch_rejected():
    with pytest.raises(ValidationError):
        req(contract={"kind": "pauli_expectations", "observables": [{"pauli": "XX", "expected": 1, "tolerance": .1}]})


# ---- Qiskit-referenced measurement mathematics
def exact(circuit, pauli):
    return float(np.real(Statevector.from_instruction(circuit.subject().native()).expectation_value(Pauli(pauli))))


def sampled(circuit, pauli, noise=Noise(), shots=20000, seed=3):
    r = execute(measurement_circuit(circuit.subject(), pauli.replace("I", "Z")), noise, shots, seed)
    return parity_expectation(r["output_counts"], shots, pauli)


def test_endianness_matches_qiskit():
    c = circ(input={"kind": "computational_basis", "bitstring": "100"}, gates=[])
    assert exact(c, "ZII") == -1 and exact(c, "IIZ") == 1  # leftmost character = qubit 2
    assert set(execute(c.subject(), Noise(), 64, 1)["output_counts"]) == {"100"}


def test_cluster_stabilizers_exact_and_sampled():
    c = circ()
    for p in ("XZI", "ZXZ", "IZX"):
        assert exact(c, p) == pytest.approx(1)
        assert sampled(c, p) == pytest.approx(1, abs=1e-9)


@pytest.mark.parametrize("prep,pauli,value", [
    ([("h", 0)], "IX", 1), ([("h", 0), ("z", 0)], "IX", -1),
    ([("h", 0), ("s", 0)], "IY", 1), ([("h", 0), ("s", 0), ("z", 0)], "IY", -1),
    ([("h", 0), ("s", 0)], "IX", 0)])
def test_x_y_z_basis_rotations(prep, pauli, value):
    c = circ(n_qubits=2, input=ZERO2, gates=gates(*prep))
    assert exact(c, pauli) == pytest.approx(value, abs=1e-12)
    assert sampled(c, pauli) == pytest.approx(value, abs=0.04)


def test_bell_correlations():
    c = circ(n_qubits=2, input=ZERO2, gates=gates(("h", 0), ("cx", (0, 1))))
    for p, v in {"ZZ": 1, "XX": 1, "YY": -1, "XZ": 0}.items():
        assert exact(c, p) == pytest.approx(v, abs=1e-12)
        assert sampled(c, p) == pytest.approx(v, abs=0.04)


def test_relative_phase_invisible_to_z_visible_to_x():
    minus = circ(n_qubits=2, input=ZERO2, gates=gates(("h", 0), ("z", 0))).model_dump(mode="json")
    plus = circ(n_qubits=2, input=ZERO2, gates=gates(("h", 0))).model_dump(mode="json")
    zc = {"kind": "measurement_distribution", "expected_probabilities": {"00": .5, "01": .5}, "tolerance": .1}
    xc = {"kind": "pauli_expectations", "observables": [{"pauli": "IX", "expected": 1, "tolerance": .1}]}
    assert investigate_lab(req(minus, zc))["diagnosis"]["category"] == "NO_SIGNIFICANT_DISCREPANCY"
    assert investigate_lab(req(minus, xc))["diagnosis"]["category"] == "SIGNIFICANT_DISCREPANCY"
    assert investigate_lab(req(plus, xc))["diagnosis"]["category"] == "NO_SIGNIFICANT_DISCREPANCY"


def test_global_phase_is_not_a_discrepancy():
    q = QuantumCircuit(2); q.h(0); q.rz(1.0, 1)
    b = QuantumCircuit(2); b.h(0); b.p(1.0, 1)  # differs from rz only by a global phase
    assert Statevector(q).equiv(Statevector(b))


def test_grouping_shares_shots_between_qubitwise_commuting_observables():
    _, groups = plan(3, PauliContract.model_validate(STAB))
    assert [g["setting"] for g in groups] == ["XZX", "ZXZ"]
    assert groups[0]["claims"] == ["obs:XZI", "obs:IZX"]


def test_noise_enabled_measurement_degrades_expectation():
    c = circ()
    assert sampled(c, "XZI", Noise(readout=0.1)) < 0.9
    assert sampled(c, "XZI", Noise(depolarizing=0.1)) < 0.99


def test_aer_conformance():
    pytest.importorskip("qiskit_aer")
    c = circ()
    r = execute(measurement_circuit(c.subject(), "XZX"), Noise(), 4000, 5, backend="aer")
    assert parity_expectation(r["output_counts"], 4000, "XZI") == pytest.approx(1)
    r = execute(measurement_circuit(c.subject(), "XZX"), Noise(readout=.1), 20000, 5, backend="aer")
    assert parity_expectation(r["output_counts"], 20000, "XZI") == pytest.approx(0.64, abs=0.04)  # (1-2p)^2


# ---- planner, budgets, accounting
def broken():
    c = copy.deepcopy(CLUSTER); c["gates"] = c["gates"][:-1]
    return c


def test_budget_never_exceeded_and_ledger_matches():
    r = investigate_lab(req(max_shots=3000, max_evaluations=6, batch_shots=512))
    assert r["cost"]["shots"] <= 3000 and r["cost"]["evaluations"] <= 6
    assert sum(e["executed_shots"] for e in r["executions"]) == r["cost"]["shots"]
    assert len(r["executions"]) == r["cost"]["circuit_executions"]


def test_insufficient_budget_is_not_called_success():
    r = investigate_lab(req(batch_shots=64, max_shots=128, max_looks=1))
    assert r["diagnosis"]["category"] == "INSUFFICIENT_EVIDENCE"
    assert not r["feasibility"]["claims"][0]["confirmable_within_tolerance"]


def test_adaptive_investigation_of_broken_cluster():
    r = investigate_lab(req(broken()))
    assert r["diagnosis"]["stop"]["code"] == "ALL_CLAIMS_RESOLVED"
    assert r["diagnosis"]["category"] == "SIGNIFICANT_DISCREPANCY"
    assert r["diagnosis"]["detection"]["violated_claims"] == ["obs:XZI", "obs:ZXZ"]
    assert "readout_control" in {e["measurement_setting"] for e in r["executions"]}
    assert r["diagnosis"]["attribution"]["status"] == "AMBIGUOUS_LOGICAL_VS_NOISE"
    assert r["diagnosis"]["localization"]["status"] == "NOT_ESTABLISHED"
    assert r["recovery"]["status"] == "UNSUPPORTED"
    assert all(a["reason_selected"] and a["shots_executed"] == a["shots_requested"] for a in r["action_ledger"])


@pytest.mark.parametrize("policy", ["adaptive", "fixed", "random", "complementary_schedule"])
def test_all_policies_respect_limits(policy):
    r = investigate_lab(req(policy=policy, max_looks=2, max_shots=6000))
    per_group = {}
    for a in r["action_ledger"]:
        g = a["measurement_specification"]["group_id"]
        per_group[g] = per_group.get(g, 0) + 1
    assert all(v <= 2 for v in per_group.values())
    assert r["cost"]["shots"] <= 6000


def test_no_false_alarm_on_correct_circuit_over_seeds():
    for seed in range(10):
        assert investigate_lab(req(seed=seed))["diagnosis"]["category"] != "SIGNIFICANT_DISCREPANCY"


def test_readout_noise_attribution_is_not_unique():
    r = investigate_lab(req(environment={"readout": 0.18, "depolarizing": 0}))
    assert r["diagnosis"]["category"] == "SIGNIFICANT_DISCREPANCY"
    assert r["diagnosis"]["attribution"]["status"] == "NOISE_CONSISTENT_NOT_UNIQUE"


def test_error_invisible_to_declared_claims_is_not_reported():
    c = copy.deepcopy(CLUSTER); c["gates"] += gates(("z", 0))
    zc = {"kind": "measurement_distribution", "expected_probabilities": {format(i, "03b"): .125 for i in range(8)}, "tolerance": .1}
    r = investigate_lab(req(c, zc))
    assert r["diagnosis"]["category"] == "NO_SIGNIFICANT_DISCREPANCY"
    assert "correctness" in r["diagnosis"]["reason"]


# ---- privilege boundary
def test_measurement_only_never_calls_privileged_state_code(monkeypatch):
    def forbidden(*a, **k):
        raise AssertionError("privileged exact-state path used in measurement-only mode")
    monkeypatch.setattr(lab, "exact_expectations", forbidden)
    monkeypatch.setattr(lab.Statevector, "from_instruction", forbidden)
    r = investigate_lab(req(broken(), diagnostic_mode="measurement_only"))
    assert r["privileged_operations"] == [] and r["cost"]["exact_state_evaluations"] == 0


def test_simulator_assisted_labels_privileged_operations_and_attribution():
    r = investigate_lab(req(broken(), diagnostic_mode="simulator_assisted"))
    assert r["privileged_operations"][0]["operation"] == "exact_expectations"
    assert r["cost"]["exact_state_evaluations"] == 1
    assert r["diagnosis"]["attribution"]["status"] == "LOGICAL_DEFECT_SUPPORTED_FIXED_INPUT"
    noisy = investigate_lab(req(diagnostic_mode="simulator_assisted", environment={"readout": .18, "depolarizing": 0}))
    assert noisy["diagnosis"]["attribution"]["status"] == "NOISE_CONSISTENT_FIXED_INPUT"
    assert noisy["diagnosis"]["attribution"]["ideal_violation_claims"] == []


def test_planner_receives_only_a_measurement_port():
    import inspect
    assert list(inspect.signature(lab.run_policy).parameters) == ["claims", "groups", "n", "expected_probs", "port", "request"]
    assert not any(hasattr(lab._Port, a) for a in ("subject", "noise", "state"))


def test_replay_is_deterministic():
    a = investigate_lab(req(broken(), seed=7))
    b = investigate_lab(LabRequest.model_validate(a["replay"]["request"]))
    assert [e["output_counts"] for e in a["executions"]] == [e["output_counts"] for e in b["executions"]]
    assert digest(a["claims"]) == digest(b["claims"])


def test_error_allocation_is_union_bound():
    d = investigate_lab(req(max_looks=4))["statistical_design"]
    assert d["alpha_per_interval"] == pytest.approx(0.01 / (3 * 4 + 1))


# ---- API and persistence
def test_api_roundtrip_persist_verify_replay_tamper(tmp_path):
    from fastapi.testclient import TestClient
    from qfault.api import create_app
    from qfault.storage import verify_export
    client = TestClient(create_app(tmp_path))
    body = {"circuit": broken(), "contract": STAB}
    v = client.post("/api/lab/validate", json=body).json()
    assert v["valid"] and v["feasibility"]["groups"][0]["setting"] == "XZX"
    assert client.post("/api/lab/validate", json={**body, "circuit": {**broken(), "gates": [{"name": "os", "qubits": [0]}]}}).status_code == 422
    assert client.post("/api/lab/investigations", json={**body, "extra": 1}).status_code == 422
    r = client.post("/api/lab/investigations", json=body)
    assert r.status_code == 201
    inv = r.json()
    eid = inv["experiment_id"]
    assert inv["diagnosis"]["category"] == "SIGNIFICANT_DISCREPANCY"
    assert "evaluation_truth" not in inv
    assert client.get(f"/api/experiments/{eid}/verification").json()["valid"]
    assert any(row["experiment_id"] == eid and row["family"] == "custom" for row in client.get("/api/experiments").json())
    report = client.get(f"/api/experiments/{eid}/report").json()
    assert verify_export(report)["valid"]
    assert report["evaluation"]["ground_truth"] is None
    again = client.post(f"/api/lab/investigations/{eid}/replay").json()
    assert [e["output_counts"] for e in again["executions"]] == [e["output_counts"] for e in inv["executions"]]
    assert client.post("/api/lab/investigations", content="x" * 70000, headers={"content-length": "70000"}).status_code == 413
    path = tmp_path / eid / "investigation.json"
    path.write_bytes(path.read_bytes().replace(b"SIGNIFICANT_DISCREPANCY", b"NO_SIGNIFICANT_DISCREPANCY", 1))
    assert not client.get(f"/api/experiments/{eid}/verification").json()["valid"]


def test_legacy_template_experiment_still_works(tmp_path):
    from fastapi.testclient import TestClient
    from qfault.api import create_app
    client = TestClient(create_app(tmp_path))
    r = client.post("/api/experiments", json={"family": "bell", "scenario": "remove", "policy": "evidence"})
    assert r.status_code == 201 and r.json()["contract"]["family"] == "bell"
