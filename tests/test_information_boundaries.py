"""Adversarial boundaries, calibrated witnesses, and request resource limits.

Backend executions are genuine; patched helpers prohibit analyst-side exact-state
access or probe the input projection without replacing measured decisions.
"""
import json
from math import sqrt

import numpy as np
import pytest
from fastapi.testclient import TestClient
from qiskit.quantum_info import Pauli

from qfault import diagnostics, lab, quantum, recovery
from qfault.api import create_app
from qfault.counterfactual import RecoveryRequest, recover
from qfault.lab import LabRequest, investigate_lab
from qfault.target import bounds, catalog, decide


def custom_body(kind="measurement_distribution", faulty=False):
    circuit = {"schema_version": 1, "name": "boundary audit", "n_qubits": 2,
               "input": {"kind": "computational_basis", "bitstring": "00"},
               "gates": [{"name": "x", "qubits": [0]}] if faulty else []}
    contracts = {
        "measurement_distribution": {"kind": "measurement_distribution",
                                     "expected_probabilities": {"00": 1.}, "tolerance": .2},
        "pauli_expectations": {"kind": "pauli_expectations",
                               "observables": [{"pauli": "IZ", "expected": 1., "tolerance": .2}]},
        "target_state": {"kind": "target_state", "amplitudes": [[1., 0.]] + [[0., 0.]] * 3,
                         "fidelity_tolerance": .25},
    }
    return {"circuit": circuit, "contract": contracts[kind]}


@pytest.mark.parametrize("length", [None, "1"])
def test_actual_request_size_is_bounded_without_trusting_header(tmp_path, length):
    payload = (json.dumps(custom_body()) + " " * 70000).encode()
    headers = {"content-type": "application/json"}
    if length is not None:
        headers["content-length"] = length
    client = TestClient(create_app(tmp_path), raise_server_exceptions=False)
    response = client.post("/api/lab/validate", content=iter([payload[:1000], payload[1000:]]), headers=headers)
    assert response.status_code == 413
    assert list(tmp_path.glob("experiment_*")) == []


@pytest.mark.parametrize("length", ["abc", "-1"])
def test_malformed_content_length_is_a_client_error(tmp_path, length):
    response = TestClient(create_app(tmp_path), raise_server_exceptions=False).post(
        "/api/lab/validate", content=json.dumps(custom_body()),
        headers={"content-type": "application/json", "content-length": length})
    assert response.status_code == 400


def test_valid_chunked_json_is_accepted(tmp_path):
    payload = json.dumps(custom_body()).encode()
    response = TestClient(create_app(tmp_path)).post(
        "/api/lab/validate", content=iter([payload[:20], payload[20:]]),
        headers={"content-type": "application/json"})
    assert response.status_code == 200
    assert response.json()["valid"]


@pytest.mark.parametrize("kind", ["pauli_expectations", "measurement_distribution", "target_state"])
def test_custom_decision_policy_cannot_receive_program_or_noise(kind, monkeypatch):
    name = "run_witness_policy" if kind == "target_state" else "run_policy"
    actual = getattr(lab, name)
    visited = []

    def checked(*args, **kwargs):
        config = args[-1]
        for field in ("circuit", "environment", "diagnostic_mode", "backend"):
            assert not hasattr(config, field), f"{name} received forbidden input {field}"
        visited.append(True)
        return actual(*args, **kwargs)

    monkeypatch.setattr(lab, name, checked)
    result = investigate_lab(LabRequest.model_validate(custom_body(kind, faulty=True)))
    assert visited
    assert result["diagnosis"]["category"] == "SIGNIFICANT_DISCREPANCY"


def forbid_exact_helpers(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Analyst used privileged candidate state")
    for module in (quantum, diagnostics, recovery):
        monkeypatch.setattr(module, "ideal_state", forbidden)
    monkeypatch.setattr(quantum, "noisy_density", forbidden)
    monkeypatch.setattr(quantum.Statevector, "from_instruction", forbidden)
    monkeypatch.setattr(lab, "exact_expectations", forbidden)
    monkeypatch.setattr(diagnostics.DiagnosticAccess, "state_probe", forbidden)
    monkeypatch.setattr(recovery.RecoveryPlanner, "propose", forbidden)


class GuardedExecution(dict):
    """Fail if any analyst consumes executor-only metadata from a real record."""
    hidden = {"evaluation_truth", "scenario", "mutation", "noise_configuration", "input_digest"}

    def __getitem__(self, key):
        assert key not in self.hidden, f"Executor metadata was consumed: {key}"
        return super().__getitem__(key)

    def get(self, key, default=None):
        assert key not in self.hidden, f"Executor metadata was consumed: {key}"
        return super().get(key, default)


@pytest.mark.parametrize("kind", ["pauli_expectations", "measurement_distribution", "target_state"])
def test_real_aer_custom_and_fresh_recovery_reject_privileged_information(kind, monkeypatch):
    pytest.importorskip("qiskit_aer")
    actual_execute = lab.execute

    def guarded_execute(*args, **kwargs):
        record = GuardedExecution(actual_execute(*args, **kwargs))
        record.update(evaluation_truth={"category": "DELIBERATELY_WRONG"}, scenario="clean", mutation={"index": 999})
        return record

    monkeypatch.setattr(lab, "execute", guarded_execute)
    forbid_exact_helpers(monkeypatch)
    body = custom_body(kind, faulty=True)
    diagnosis = investigate_lab(LabRequest.model_validate({**body, "backend": "aer"}))
    assert diagnosis["diagnosis"]["category"] == "SIGNIFICANT_DISCREPANCY"
    assert diagnosis["privileged_operations"] == []
    repaired = recover(RecoveryRequest.model_validate({**body, "backend": "aer", "max_candidates": 4}))
    assert repaired["status"] == "VERIFIED_UNDER_DECLARED_CONTRACT"
    assert repaired["privileged_operations"] == []
    assert repaired["localization"]["causal_origin"] == "NOT_IDENTIFIED"
    selection = repaired["selection"]
    assert selection["frozen_before_verification"]
    phases = {}
    for record in repaired["executions"]:
        phases.setdefault(record["recovery_phase"], set()).add(record["execution_id"])
    assert phases["verification_original"].isdisjoint(phases["observation"])
    assert phases["verification_candidate"].isdisjoint(phases["screening"])
    assert len({r["seed"] for r in repaired["executions"]}) == len(repaired["executions"])


@pytest.mark.parametrize("threshold", [.7, .9])
def test_basis_gate_noise_does_not_define_a_common_observed_state(threshold):
    """Exact Qiskit counterexample: true means can yield mutually inconsistent bounds."""
    c = quantum.benchmark("bell", 2)
    noise = quantum.Noise(depolarizing=.05)
    means = {}
    for label in ("XX", "YY", "ZZ"):
        analyzed = lab.measurement_circuit(c, label)
        rho = quantum.noisy_density(analyzed, noise)
        means[label] = float(np.real(rho.expectation_value(Pauli("ZZ"))))
    assert means == pytest.approx({"XX": .95**4, "YY": -.95**6, "ZZ": .95})
    reconstructed = (np.eye(4) + sum(means[p] * Pauli(p).to_matrix() for p in means)) / 4
    assert np.linalg.eigvalsh(reconstructed)[0] < -.007
    s = 1 / sqrt(2)
    cat = catalog(((s, 0.), (0., 0.), (0., 0.), (s, 0.)))
    lo, hi = bounds(cat, means, {p: 0. for p in means})
    assert lo > hi  # No interval missed its mean; the common-state model failed.
    assert decide(lo, hi, threshold) == "UNRESOLVED"


@pytest.mark.parametrize("environment", [{"depolarizing": .05}, {"readout": .1}])
def test_noisy_target_witness_does_not_certify_preanalysis_state(environment):
    body = custom_body("target_state")
    result = investigate_lab(LabRequest.model_validate({**body, "environment": environment}))
    assert result["claims"][0]["status"] == "UNRESOLVED"
    assert result["diagnosis"]["category"] == "INSUFFICIENT_EVIDENCE"
    assert result["target_evidence"]["model_validity"] == "CALIBRATION_REQUIRED"


def test_noisy_target_recovery_abstains_before_uncalibrated_certification():
    result = recover(RecoveryRequest.model_validate({**custom_body("target_state", faulty=True),
                                                    "environment": {"depolarizing": .05}}))
    assert result["status"] == "MEASUREMENT_MODEL_ABSTENTION"
    assert result["selected_candidate"] is None
    assert result["verification"]["status"] != "VERIFIED_UNDER_DECLARED_CONTRACT"
