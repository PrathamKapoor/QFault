"""Prespecified target-state witness corpus (separate from the 117-case custom-lab corpus).

Targets are declared from the intended REFERENCE design (exact Qiskit evaluation of the reference
circuit) or analytically; never from the candidate. Candidates are the reference with one declared
modification and/or a simulated environment. Truth is computed evaluator-side only.
"""
from math import pi
import numpy as np
from qiskit.quantum_info import DensityMatrix, Pauli, Statevector
from .lab import CustomCircuit
from .quantum import Noise, noisy_density
from .target import TargetStateContract, catalog, fidelity

TOLERANCE = 0.2


def _g(name, *q, angle=None):
    return {"name": name, "qubits": list(q), **({"angle": angle} if angle is not None else {})}


def reference(family, n):
    """(input bitstring, gates). Families differ structurally, not just in parameters."""
    if family == "ghz":
        return "0" * n, [_g("h", 0)] + [_g("cx", 0, q) for q in range(1, n)]
    if family == "line_graph":
        return "0" * n, [_g("h", q) for q in range(n)] + [_g("cz", q, q + 1) for q in range(n - 1)]
    if family == "star_graph":
        return "0" * n, [_g("h", q) for q in range(n)] + [_g("cz", 0, q) for q in range(1, n)]
    if family == "complex_product":  # |+i>, |->, ry(pi/3), ... : Y-sensitive, relative phases
        g = [_g("h", 0), _g("s", 0), _g("x", 1), _g("h", 1)]
        return "0" * n, g + [_g("ry", q, angle=pi / 3) for q in range(2, n)]
    if family == "clifford_mix":
        return "0" * n, [_g("h", 0), _g("s", 0), _g("cx", 0, 1), _g("h", 1)] + [_g("cz", 1, q) for q in range(2, n)]
    if family == "rotation_entangler":  # non-Clifford: dense Pauli expansion
        g = [_g("ry", q, angle=0.4 + 0.3 * q) for q in range(n)] + [_g("cx", q, q + 1) for q in range(n - 1)]
        return "0" * n, g + [_g("rz", n - 1, angle=0.9), _g("rx", 0, angle=0.5)]
    if family == "inverse_echo":  # U then U^dagger: target is the declared input itself (analytic)
        fwd = [_g("h", 0), _g("cx", 0, 1), _g("ry", 1, angle=0.7)] + [_g("cx", 1, q) for q in range(2, n)]
        inv = [_g("cx", 1, q) for q in reversed(range(2, n))] + [_g("ry", 1, angle=-0.7), _g("cx", 0, 1), _g("h", 0)]
        return "0" * (n - 1) + "1", fwd + inv
    raise ValueError(family)


def circuit(n, bits, gates, name):
    return {"schema_version": 1, "name": name, "n_qubits": n,
            "input": {"kind": "computational_basis", "bitstring": bits}, "gates": gates}


def declare_target(family, n, bits, gates, phase=0.0):
    if family == "inverse_echo":
        v = np.zeros(2 ** n, complex); v[int(bits, 2)] = 1; provenance = "analytic: echo returns declared input"
    else:
        ref = CustomCircuit.model_validate(circuit(n, bits, gates, "reference"))
        v = Statevector.from_instruction(ref.subject().native()).data; provenance = "exact Qiskit evaluation of reference design"
    v = v * np.exp(1j * phase)
    return {"kind": "target_state", "fidelity_tolerance": TOLERANCE, "provenance": provenance,
            "amplitudes": [[float(z.real), float(z.imag)] for z in v]}


def modifications(gates):
    out = {"clean": gates, "remove_last": gates[:-1], "extra_s": gates + [_g("s", 0)],
           "extra_z_q1": gates + [_g("z", 1)]}
    for i, g in enumerate(gates):
        if "angle" in g:
            out["angle_small"] = gates[:i] + [{**g, "angle": g["angle"] + 0.3}] + gates[i + 1:]
            out["angle_large"] = gates[:i] + [{**g, "angle": g["angle"] + 1.2}] + gates[i + 1:]
            break
    return out


ENVIRONMENTS = {"ideal": {"readout": 0.0, "depolarizing": 0.0},
                "readout": {"readout": 0.04, "depolarizing": 0.0},
                "gate_noise": {"readout": 0.0, "depolarizing": 0.05}}
BUDGETS = {"tight": {"batch_shots": 1024, "max_shots": 12288, "max_evaluations": 24, "max_looks": 4, "alpha_total": 0.01},
           "ample": {"batch_shots": 1024, "max_shots": 32768, "max_evaluations": 40, "max_looks": 4, "alpha_total": 0.01}}
SPLITS = {  # frozen in configs/target-witness-protocol.json before the holdout is executed
    "development": {"families": [("ghz", 3), ("line_graph", 3), ("complex_product", 2), ("rotation_entangler", 2), ("inverse_echo", 2)],
                    "seeds": [301, 302]},
    "holdout": {"families": [("ghz", 4), ("star_graph", 4), ("clifford_mix", 3), ("complex_product", 3),
                             ("rotation_entangler", 3), ("inverse_echo", 3), ("line_graph", 2)],
                "seeds": [7101, 7102, 7103]},
}


def cases(split):
    out = []
    for family, n in SPLITS[split]["families"]:
        bits, ref = reference(family, n)
        for mod, gates in modifications(ref).items():
            envs = list(ENVIRONMENTS) if mod == "clean" else ["ideal"]
            phases = [0.0, 2.1] if mod == "clean" else [0.0]  # global-phase negative control
            for env in envs:
                for phase in phases:
                    for budget in BUDGETS:
                        for seed in SPLITS[split]["seeds"]:
                            out.append({"case_id": f"{split}:{family}{n}:{mod}:{env}:phase{phase}:{budget}:{seed}",
                                        "family": family, "n": n, "modification": mod, "environment": env,
                                        "global_phase": phase, "budget": budget, "seed": seed,
                                        "circuit": circuit(n, bits, gates, f"{family}-{n}-{mod}"),
                                        "contract": declare_target(family, n, bits, ref, phase),
                                        "environment_noise": ENVIRONMENTS[env]})
    return out


def _local_depolarize(rho, lam, n):
    """Readout flip p on every qubit acts on measured Pauli expectations as local depolarizing lambda=1-2p."""
    out = rho.data * 0
    for k in range(4 ** n):
        label = "".join("IXYZ"[(k >> (2 * j)) & 3] for j in range(n))
        P = Pauli(label).to_matrix()
        out = out + np.real(np.trace(P @ rho.data)) * lam ** sum(c != "I" for c in label) * P
    return DensityMatrix(out / 2 ** n)


def truth(case):
    """Evaluator-side: ideal fidelity, and effective fidelity where the measured quantity is a state property."""
    c = CustomCircuit.model_validate(case["circuit"])
    t = TargetStateContract.model_validate(case["contract"])
    ideal = fidelity(t.vector(), Statevector.from_instruction(c.subject().native()))
    env = case["environment_noise"]
    effective, gate_state = None, None
    if env["depolarizing"] == 0:  # basis-gate noise would make the measured quantity basis-dependent
        rho = DensityMatrix(Statevector.from_instruction(c.subject().native()))
        if env["readout"]:
            rho = _local_depolarize(rho, 1 - 2 * env["readout"], c.n_qubits)
        effective = fidelity(t.vector(), rho)
    else:
        gate_state = fidelity(t.vector(), noisy_density(c.subject(), Noise(depolarizing=env["depolarizing"])))
    cat = catalog(t.amplitudes)
    thr = t.threshold
    cls = "logical_violation" if ideal < thr else ("noise_only" if env != ENVIRONMENTS["ideal"] else "clean_correct")
    return {"ideal_fidelity": ideal, "effective_fidelity": effective, "gate_noise_state_fidelity": gate_state, "threshold": thr, "class": cls,
            "effective_violation": None if effective is None else effective < thr,
            "catalog_terms": len(cat["terms"]), "stabilizer_target": cat["stabilizer"]}
