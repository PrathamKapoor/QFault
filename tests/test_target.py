"""Target-state contracts: Qiskit-referenced mathematics, bound validity, adaptivity, privilege boundary."""
import copy
import itertools
from math import sqrt
import numpy as np
import pytest
from pydantic import ValidationError
from qiskit.quantum_info import DensityMatrix, Pauli, Statevector, random_density_matrix, random_statevector, state_fidelity
import qfault.lab as lab
from qfault.lab import LabRequest, investigate_lab
from qfault.target import TargetStateContract, bounds, catalog, decide, fidelity, marginal_gains

S = 1 / sqrt(2)
BELL_T = {"kind": "target_state", "amplitudes": [[S, 0], [0, 0], [0, 0], [S, 0]], "fidelity_tolerance": 0.25}
BELL_C = {"schema_version": 1, "name": "bell", "n_qubits": 2, "input": {"kind": "computational_basis", "bitstring": "00"},
          "gates": [{"name": "h", "qubits": [0]}, {"name": "cx", "qubits": [0, 1]}]}


def amps(v):
    return [[float(z.real), float(z.imag)] for z in np.asarray(v)]


def req(circuit=BELL_C, contract=BELL_T, **kw):
    return LabRequest.model_validate({"circuit": circuit, "contract": contract, **kw})


# ---- validation and identity
@pytest.mark.parametrize("bad", [
    {"amplitudes": [[1, 0], [0, 0], [0, 0]]},                      # not a power of two
    {"amplitudes": [[1, 0], [1, 0], [0, 0], [0, 0]]},              # unnormalized (|psi|^2 = 2)
    {"amplitudes": [[0, 0]] * 4},                                  # zero vector
    {"amplitudes": [[float("nan"), 0], [0, 0], [0, 0], [1, 0]]},   # non-finite
    {"amplitudes": [[1, 0, 0], [0, 0], [0, 0], [0, 0]]},           # malformed complex pair
    {"amplitudes": [["1", 0], [0, 0], [0, 0], [0, 0]]},            # expression/string, not a number
    {"fidelity_tolerance": 0}, {"fidelity_tolerance": 1.5},
    {"extra": 1},
])
def test_invalid_targets_rejected(bad):
    with pytest.raises(ValidationError):
        TargetStateContract.model_validate({**BELL_T, **bad})


def test_target_length_must_match_circuit():
    three = [[1, 0]] + [[0, 0]] * 7
    with pytest.raises(ValidationError):
        req(contract={**BELL_T, "amplitudes": three})


def test_small_norm_deviation_accepted_and_renormalized():
    t = TargetStateContract.model_validate({**BELL_T, "amplitudes": [[S * (1 + 2e-7), 0], [0, 0], [0, 0], [S, 0]]})
    assert np.linalg.norm(t.vector()) == pytest.approx(1, abs=1e-15)


def test_stable_contract_identity():
    a = req().model_dump(mode="json")["contract"]; b = req().model_dump(mode="json")["contract"]
    assert a == b


def test_witness_policies_require_target_contract():
    with pytest.raises(ValidationError):
        LabRequest.model_validate({"circuit": BELL_C, "policy": "adaptive_witness",
            "contract": {"kind": "pauli_expectations", "observables": [{"pauli": "ZZ", "expected": 1, "tolerance": .1}]}})
    with pytest.raises(ValidationError):
        req(policy="adaptive")
    assert req().policy == "adaptive_witness"  # default for target contracts


# ---- fidelity, global phase, Qiskit cross-checks
@pytest.mark.parametrize("phase", [1, -1, 1j, np.exp(0.731j)])
def test_global_phase_invariance(phase):
    v = random_statevector(8, seed=3).data
    assert fidelity(v, phase * v) == pytest.approx(1, abs=1e-12)
    t = TargetStateContract.model_validate({**BELL_T, "amplitudes": amps(phase * np.array([S, 0, 0, S]))})
    assert investigate_lab(req(contract=t.model_dump()))["diagnosis"]["category"] == "NO_SIGNIFICANT_DISCREPANCY"


def test_relative_phase_orthogonal_and_mixed_fidelity_match_qiskit():
    plus, minus = np.array([S, 0, 0, S]), np.array([S, 0, 0, -S])
    assert fidelity(plus, minus) == pytest.approx(0, abs=1e-15)
    for seed in range(5):
        t, s = random_statevector(4, seed=seed), random_statevector(4, seed=seed + 50)
        rho = random_density_matrix(4, seed=seed)
        assert fidelity(t.data, s) == pytest.approx(state_fidelity(t, s), abs=1e-12)
        assert fidelity(t.data, rho) == pytest.approx(state_fidelity(t, rho), abs=1e-12)


def test_pauli_decomposition_reconstructs_target_and_fidelity():
    for n, seed in [(2, 1), (3, 2)]:
        v = random_statevector(2 ** n, seed=seed)
        cat = catalog(tuple(map(tuple, amps(v.data))))
        d = 2 ** n
        rho = np.eye(d, dtype=complex) / d + sum(a * Pauli(l).to_matrix() for l, a in cat["terms"]) / d
        assert np.allclose(rho, DensityMatrix(v).data, atol=1e-10)
        for label, a in cat["terms"]:  # endianness: coefficients equal Qiskit expectation values
            assert a == pytest.approx(float(np.real(v.expectation_value(Pauli(label)))), abs=1e-10)
        sigma = random_density_matrix(d, seed=seed)
        b = {l: float(np.real(sigma.expectation_value(Pauli(l)))) for l, _ in cat["terms"]}
        F = (1 + sum(a * b[l] for l, a in cat["terms"])) / d
        assert F == pytest.approx(state_fidelity(v, sigma), abs=1e-10)
        exact = bounds(cat, b, {l: 0. for l in b})
        assert exact[0] == pytest.approx(F, abs=1e-9) and exact[1] >= F - 1e-9


def test_stabilizer_detection_and_sparse_vs_dense():
    ghz = catalog(tuple(map(tuple, amps(np.array([S, 0, 0, 0, 0, 0, 0, S])))))
    assert ghz["stabilizer"] and len(ghz["terms"]) == 7 and ghz["omitted_abs_bound"] < 1e-6
    dense = catalog(tuple(map(tuple, amps(random_statevector(8, seed=9).data))))
    assert not dense["stabilizer"] and len(dense["terms"]) > 30


# ---- bound validity (deterministic coverage given covering intervals)
def test_bounds_contain_true_fidelity_for_any_covering_intervals():
    rng = np.random.default_rng(0)
    for trial in range(300):
        n = 2 if trial % 2 else 3
        d = 2 ** n
        tv = random_statevector(d, seed=trial) if trial % 3 else Statevector(np.array([S] + [0] * (d - 2) + [S]))
        cat = catalog(tuple(map(tuple, amps(tv.data))))
        rho = random_density_matrix(d, seed=1000 + trial, rank=int(rng.integers(1, 3)))
        F = state_fidelity(tv, rho)
        measured = [l for l, _ in cat["terms"] if rng.random() < .6]
        est, rad = {}, {}
        for l in measured:
            true = float(np.real(rho.expectation_value(Pauli(l))))
            r = float(rng.uniform(0, .3))
            est[l], rad[l] = true + float(rng.uniform(-r, r)), r
        L, U = bounds(cat, est, rad)
        assert -1e-9 <= L <= F + 1e-9 and F - 1e-9 <= U <= 1 + 1e-9, (trial, L, F, U)


def test_partial_witness_never_claims_exact_fidelity():
    cat = catalog(tuple(map(tuple, amps(np.array([S, 0, 0, S])))))
    L, U = bounds(cat, {"XX": 1.0}, {"XX": 0.0})
    assert (L, U) != (1.0, 1.0) and decide(L, U, .75) == "UNRESOLVED"


def test_sampled_bounds_cover_effective_fidelity_under_readout_noise():
    p = 0.1  # readout flip p == local depolarizing lambda=1-2p on measured Paulis
    f_eff = (1 + 3 * (1 - 2 * p) ** 2) / 4
    for seed in range(12):
        r = investigate_lab(req(environment={"readout": p, "depolarizing": 0}, seed=seed, max_shots=16384,
                                contract={**BELL_T, "fidelity_tolerance": 0.2}))
        L, U = r["target_evidence"]["fidelity_bound"]
        assert L <= f_eff <= U


# ---- adaptivity and planning
def test_observed_data_change_the_next_witness():
    cat = catalog(tuple(map(tuple, amps(np.array([S, 0, 0, S])))))
    groups, radii = [["XX"], ["YY"], ["ZZ"]], [.08, .1, .1]
    consistent, d1 = marginal_gains(cat, {"XX": 1.0}, {"XX": .1}, groups, radii, .75)
    deviating, d2 = marginal_gains(cat, {"XX": -0.5}, {"XX": .1}, groups, radii, .75)
    pick = lambda g: max(range(3), key=lambda i: g[i])
    assert (d1, d2) == ("confirm", "violate")
    assert pick(consistent) != 0 and pick(deviating) == 0


def test_end_to_end_adaptive_actions_respond_to_evidence():
    good = investigate_lab(req())
    bad = investigate_lab(req(circuit={**BELL_C, "gates": BELL_C["gates"][:1]}))
    assert good["diagnosis"]["category"] == "NO_SIGNIFICANT_DISCREPANCY"
    assert bad["diagnosis"]["category"] == "SIGNIFICANT_DISCREPANCY"
    assert bad["target_evidence"]["witness_discrepancies"]
    assert all("aiming to" in a["reason_selected"] for a in good["action_ledger"] + bad["action_ledger"])


@pytest.mark.parametrize("policy", ["adaptive_witness", "coefficient_weighted", "fixed", "random", "complementary_schedule"])
def test_budget_and_ledger_accounting(policy):
    c3 = {**BELL_C, "n_qubits": 3, "input": {"kind": "computational_basis", "bitstring": "000"},
          "gates": [{"name": "ry", "qubits": [q], "angle": .3 + q} for q in range(3)] + [{"name": "cx", "qubits": [0, 1]}]}
    # Correct circuit, dense non-stabilizer target from an independent reference evaluation of the intended design.
    ref = lab.CustomCircuit.model_validate(c3).subject().native()
    dense = {**BELL_T, "amplitudes": amps(Statevector(ref).data), "fidelity_tolerance": .1}
    r = investigate_lab(req(c3, dense, policy=policy, max_shots=4096, batch_shots=512, max_evaluations=6))
    assert r["cost"]["shots"] <= 4096 and r["cost"]["evaluations"] <= 6
    assert sum(e["executed_shots"] for e in r["executions"]) == r["cost"]["shots"]
    assert r["diagnosis"]["category"] == "INSUFFICIENT_EVIDENCE"  # dense target, tiny budget: honest abstention
    assert not r["feasibility"]["claims"][0]["confirmable_within_tolerance"]
    for a in r["action_ledger"]:
        assert a["seed"] is not None and a["measurement_specification"]["pauli_terms"]


def test_error_allocation_counts_every_catalog_term():
    r = investigate_lab(req(max_looks=3))
    assert r["statistical_design"]["alpha_per_interval"] == pytest.approx(0.01 / (3 * 3 + 1))


# ---- capability boundary
def test_measurement_only_target_run_never_touches_candidate_state(monkeypatch):
    def forbidden(*a, **k):
        raise AssertionError("privileged candidate-state path used")
    monkeypatch.setattr(lab, "exact_expectations", forbidden)
    monkeypatch.setattr(lab.Statevector, "from_instruction", forbidden)
    monkeypatch.setattr("qfault.quantum.noisy_density", forbidden)
    r = investigate_lab(req(circuit={**BELL_C, "gates": BELL_C["gates"][:1]}))
    assert r["privileged_operations"] == [] and "exact" not in r["target_evidence"]
    assert r["target_evidence"]["label"] == "MEASUREMENT_DERIVED_WITNESS"


def test_simulator_assisted_reports_exact_fidelity_separately():
    r = investigate_lab(req(circuit={**BELL_C, "gates": BELL_C["gates"][:1]}, diagnostic_mode="simulator_assisted",
                            environment={"readout": 0, "depolarizing": .1}))
    ex = r["target_evidence"]["exact"]
    assert ex["label"] == "SIMULATOR_ASSISTED_EXACT_STATE" and ex["ideal_fidelity"] == pytest.approx(.25)  # |<Phi+|+0>|^2
    # depolarized H on |0> keeps <0|rho|0> = 1/2, so this candidate's noisy fidelity is also exactly 1/4
    assert ex["gate_noise_state_fidelity"] == pytest.approx(.25)
    noisy = investigate_lab(req(diagnostic_mode="simulator_assisted", environment={"readout": 0, "depolarizing": .1}))
    assert noisy["target_evidence"]["exact"]["ideal_fidelity"] == pytest.approx(1)
    assert noisy["target_evidence"]["exact"]["gate_noise_state_fidelity"] < .95
    assert r["diagnosis"]["attribution"]["status"] == "LOGICAL_DEFECT_SUPPORTED_FIXED_INPUT"


def test_api_target_roundtrip(tmp_path):
    from fastapi.testclient import TestClient
    from qfault.api import create_app
    from qfault.storage import verify_export
    client = TestClient(create_app(tmp_path))
    body = {"circuit": BELL_C, "contract": BELL_T}
    v = client.post("/api/lab/validate", json=body).json()
    assert v["feasibility"]["catalog"]["stabilizer_target"] and v["feasibility"]["claims"][0]["confirmable_within_tolerance"]
    assert client.post("/api/lab/validate", json={**body, "contract": {**BELL_T, "amplitudes": [[1, 0]] * 4}}).status_code == 422
    inv = client.post("/api/lab/investigations", json=body).json()
    eid = inv["experiment_id"]
    assert "exact" not in inv["target_evidence"] and inv["privileged_operations"] == []
    report = client.get(f"/api/experiments/{eid}/report").json()
    assert verify_export(report)["valid"]
    again = client.post(f"/api/lab/investigations/{eid}/replay").json()
    assert [e["output_counts"] for e in again["executions"]] == [e["output_counts"] for e in inv["executions"]]
