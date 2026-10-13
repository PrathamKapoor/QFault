"""Prespecified custom-circuit benchmark cases.

Every contract is declared from the REFERENCE design (the intended circuit) by exact Qiskit
evaluation, never from the candidate under test. Candidates are the reference with one
declared modification and/or a simulated execution environment. Truth is evaluator-side only.
"""
from itertools import product
from math import pi
import numpy as np
from qiskit.quantum_info import Pauli, Statevector
from .lab import CustomCircuit, LabRequest, DistributionContract, exact_expectations

ZERO = lambda n: {"kind": "computational_basis", "bitstring": "0" * n}


def _g(name, *qubits, angle=None):
    return {"name": name, "qubits": list(qubits), **({"angle": angle} if angle is not None else {})}


def reference(family, variant):
    """Return (n, input_bitstring, gates, contract_kind)."""
    if family == "cluster":  # linear graph state, H on all then CZ chain
        n = variant
        return n, "0" * n, [_g("h", q) for q in range(n)] + [_g("cz", q, q + 1) for q in range(n - 1)], "pauli"
    if family == "product_phase":  # |+y>, |-x>, ry-rotated qubits: Z-only blind
        n = variant
        gates = [_g("h", 0), _g("s", 0), _g("h", 1), _g("z", 1)] + [_g("ry", q, angle=pi / 2) for q in range(2, n)]
        return n, "0" * n, gates, "pauli"
    if family == "clifford":  # H,S,CX chain: (|0..0> + i|1..1>)/sqrt2
        n = variant
        return n, "0" * n, [_g("h", 0), _g("s", 0)] + [_g("cx", q, q + 1) for q in range(n - 1)], "pauli"
    if family == "echo":  # U then U^dagger on input |0..01>; identity-on-one-input contract
        n = variant
        fwd = [_g("h", 0), _g("cx", 0, 1), _g("rz", 1, angle=0.7)] + ([_g("cx", 1, 2)] if n > 2 else [])
        inv = [_g("cx", 1, 2)] if n > 2 else []
        inv += [_g("rz", 1, angle=-0.7), _g("cx", 0, 1), _g("h", 0)]
        return n, "0" * (n - 1) + "1", fwd + inv, "distribution"
    raise ValueError(family)


def _circuit(n, bits, gates, name):
    return {"schema_version": 1, "name": name, "n_qubits": n,
            "input": {"kind": "computational_basis", "bitstring": bits}, "gates": gates}


def declare_contract(n, bits, gates, kind, tolerance=0.1):
    ref = CustomCircuit.model_validate(_circuit(n, bits, gates, "reference"))
    if kind == "distribution":
        return {"kind": "measurement_distribution", "basis": "Z", "tolerance": tolerance,
                "expected_probabilities": {bits: 1.0}}
    state = Statevector.from_instruction(ref.subject().native())
    scored = []
    for letters in product("IXYZ", repeat=n):
        label = "".join(letters)
        if set(label) == {"I"}:
            continue
        v = float(np.real(state.expectation_value(Pauli(label))))
        if abs(abs(v) - 1) < 1e-9:
            scored.append((-sum(c in "XY" for c in label), -sum(c != "I" for c in label), label, round(v)))
    scored.sort()
    chosen, seen = [], set()
    for _, _, label, v in scored:  # prefer phase-sensitive, high-weight stabilizers; then limit to n generators
        chosen.append({"pauli": label, "expected": float(v), "tolerance": tolerance})
        if len(chosen) == n:
            break
    return {"kind": "pauli_expectations", "observables": chosen}


def modifications(gates, n):
    """Declared one-edit candidate modifications of the reference gate list."""
    out = {"clean": gates, "remove_last": gates[:-1], "remove_first": gates[1:]}
    out["extra_z"] = [_g("z", 0)] + gates
    for i, g in enumerate(gates):
        if "angle" in g:
            for name, delta in (("angle_shift", pi / 3), ("angle_edge", 0.5), ("angle_small", 0.25)):
                out[name] = gates[:i] + [{**g, "angle": g["angle"] + delta}] + gates[i + 1:]
            break
    else:
        out["swap_gate"] = [dict(g, name="cz") if g["name"] == "cx" else g for g in gates]
    return out


ENVIRONMENTS = {"ideal": {"readout": 0.0, "depolarizing": 0.0},
                "readout": {"readout": 0.15, "depolarizing": 0.0},
                "gate_noise": {"readout": 0.0, "depolarizing": 0.15}}

SPLITS = {  # prespecified before the policy comparison was run; no later edits
    "development": {"families": [("cluster", 3), ("product_phase", 3), ("echo", 2)], "seeds": [101, 102, 103]},
    "holdout": {"families": [("cluster", 4), ("cluster", 5), ("clifford", 3), ("product_phase", 4), ("echo", 3)],
                "seeds": [9001, 9002, 9003]},
}


def cases(split):
    out = []
    spec = SPLITS[split]
    for family, variant in spec["families"]:
        n, bits, ref_gates, kind = reference(family, variant)
        contract = declare_contract(n, bits, ref_gates, kind)
        for mod, gates in modifications(ref_gates, n).items():
            envs = ["ideal"] if mod != "clean" else list(ENVIRONMENTS)
            for env in envs:
                for seed in spec["seeds"]:
                    out.append({"case_id": f"{split}:{family}{variant}:{mod}:{env}:{seed}", "family": family,
                                "variant": variant, "modification": mod, "environment": env, "seed": seed,
                                "circuit": _circuit(n, bits, gates, f"{family}-{variant}-{mod}"),
                                "reference_gates": ref_gates, "contract": contract,
                                "environment_noise": ENVIRONMENTS[env]})
    return out


def truth(case):
    """Evaluator-side label: does the candidate's ideal state violate the declared claims?"""
    request = LabRequest.model_validate({"circuit": case["circuit"], "contract": case["contract"]})
    exact = exact_expectations(request.circuit, request.contract)
    violated = []
    for claim_id, value in exact.items():
        if claim_id.startswith("dist:"):
            tolerance = request.contract.tolerance
            violated.append(value > tolerance)
        else:
            observable = next(o for o in request.contract.observables if "obs:" + o.pauli == claim_id)
            violated.append(abs(value - observable.expected) > observable.tolerance)
    noisy = case["environment"] != "ideal"
    return {"ideal_violation": any(violated), "noise": noisy, "modification": case["modification"],
            "environment": case["environment"],
            "class": "logical_fault" if any(violated) else ("noise_only" if noisy else "clean_correct")}
