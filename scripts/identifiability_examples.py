"""Explicit Qiskit identifiability counterexamples, with exclusive output.

Run: python -m scripts.identifiability_examples --out benchmarks/identifiability-v1.json

This is a reproducible demonstration, not an untouched validation corpus. Exact
states and channels are labelled evaluator or executor operations. They never
become features of a QFAULT measurement-only diagnosis.
"""
import argparse
import hashlib
from importlib.metadata import version
from itertools import combinations
from pathlib import Path
import platform

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, Kraus, Operator, Statevector

from qfault.evidence import canonical, digest
from qfault.lab import basis_rotation, measurement_circuit
from qfault.quantum import Circuit, Gate, Noise, benchmark, execute, resources

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILES = ("scripts/identifiability_examples.py", "qfault/quantum.py", "qfault/backends.py",
                "qfault/lab.py", "qfault/evidence.py", "pyproject.toml")
X = np.array([[0., 1.], [1., 0.]], dtype=complex)


def source_hashes():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCE_FILES}


def density(circuit):
    """EVALUATOR ORACLE: exact fixed-input state, not a measured feature."""
    return DensityMatrix(Statevector.from_instruction(circuit.native()))


def probabilities(rho, setting):
    """EVALUATOR ORACLE: exact calibrated POVM probabilities."""
    rotated = rho.evolve(basis_rotation(setting, rho.num_qubits).native())
    return {format(i, f"0{rho.num_qubits}b"): float(p) for i, p in enumerate(rotated.probabilities())}


def tv(a, b):
    return float(sum(abs(a.get(k, 0.) - b.get(k, 0.)) for k in a.keys() | b.keys()) / 2)


def subject(name, circuit, **extra):
    return {"name": name, "circuit_id": circuit.circuit_id, "circuit": circuit.model_dump(mode="json"),
            "resources": resources(circuit), **extra}


def explicit_channel_density():
    """Executor/evaluator reference model for a channel outside QFAULT's noise schema."""
    return DensityMatrix.from_label("00").evolve(Kraus([X]), qargs=[0])


class Measurements:
    def __init__(self, shot_grid, seed, backends):
        self.shot_grid, self.seed, self.backends = shot_grid, seed, backends
        self.records = []

    def collect(self, case_id, subjects, settings, noise_by_subject=None, channel_subject=None):
        ids = []
        for backend in self.backends:
            for shots in self.shot_grid:
                for name, circuit in subjects:
                    for setting in settings:
                        seed = (self.seed + 7919 * len(self.records)) % 2**32
                        noise = (noise_by_subject or {}).get(name, Noise())
                        if name == channel_subject:
                            record = self.custom_channel(setting, shots, seed, backend)
                        else:
                            record = execute(measurement_circuit(circuit, setting), noise, shots, seed, backend=backend)
                        measurement_id = f"measurement{len(self.records):04d}"
                        self.records.append({"measurement_id": measurement_id, "example_id": case_id,
                            "subject": name, "setting": setting, "backend": backend,
                            "backend_name": record["backend_name"], "shots": record["executed_shots"],
                            "seed": seed, "counts": record["output_counts"],
                            "execution_status": record["execution_status"], "resources": record["resources"],
                            "noise_configuration": noise.model_dump() if name != channel_subject else None,
                            "channel_model": "explicit deterministic X Kraus channel" if name == channel_subject else None})
                        ids.append(measurement_id)
        return ids

    @staticmethod
    def custom_channel(setting, shots, seed, backend):
        """Genuine reference/Aer sampling of E(rho)=X rho X, separate from QFAULT Noise."""
        q = QuantumCircuit(2)
        q.append(Kraus([X]).to_instruction(), [0])
        q.compose(basis_rotation(setting, 2).native(), inplace=True)
        res = {"depth": q.depth(), "gates": len(q.data), "two_qubit_gates": 0, "qubits": 2}
        if backend == "reference":
            rho = explicit_channel_density().evolve(basis_rotation(setting, 2).native())
            rho.seed(seed)
            counts = {str(k): int(v) for k, v in rho.sample_counts(shots).items()}
            name = "qiskit.quantum_info.DensityMatrix.sample_counts/explicit_Kraus"
        else:
            from qiskit_aer import AerSimulator
            q.measure_all()
            result = AerSimulator(method="density_matrix", max_parallel_threads=1).run(
                q, shots=shots, seed_simulator=seed).result()
            if not result.success:
                raise RuntimeError("Explicit-channel Aer demonstration failed")
            counts = {str(k): int(v) for k, v in result.get_counts().items()}
            name = "qiskit_aer.AerSimulator/density_matrix/explicit_Kraus"
        if sum(counts.values()) != shots:
            raise RuntimeError("Explicit-channel shot accounting mismatch")
        return {"backend_name": name, "executed_shots": shots, "output_counts": counts,
                "execution_status": "SUCCEEDED", "resources": res}


def build_report(shot_grid=(256, 4096), seed=20261016, backends=("reference", "aer")):
    if (len(shot_grid) < 2 or any(type(n) is not int or not 1 <= n <= 100000 for n in shot_grid)
            or list(shot_grid) != sorted(set(shot_grid))):
        raise ValueError("shot grid must contain at least two strictly increasing integer sizes in [1,100000]")
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("seed must be a uint32")
    if not backends or len(set(backends)) != len(backends) or set(backends) - {"reference", "aer"}:
        raise ValueError("backends must be unique reference/aer selections")
    before = source_hashes()
    m = Measurements(tuple(shot_grid), seed, tuple(backends))
    examples = []

    plus = benchmark("bell", 2)
    minus = Circuit(n_qubits=2, gates=plus.gates + (Gate(name="z", qubits=(0,)),))
    rplus, rminus = density(plus), density(minus)
    zplus, zminus = probabilities(rplus, "ZZ"), probabilities(rminus, "ZZ")
    xplus, xminus = probabilities(rplus, "XX"), probabilities(rminus, "XX")
    phase = "phase_visibility"
    examples.append({"example_id": phase, "subjects": [subject("bell_plus", plus), subject("bell_minus", minus)],
        "evaluator_oracle": {"label": "PRIVILEGED_EXACT_STATE_AND_POVM",
            "z_distributions": {"bell_plus": zplus, "bell_minus": zminus},
            "xx_distributions": {"bell_plus": xplus, "bell_minus": xminus},
            "z_total_variation": tv(zplus, zminus), "xx_total_variation": tv(xplus, xminus),
            "state_fidelity": float(np.real(np.trace(rplus.data @ rminus.data)))},
        "identifiability": {"z_only": "RELATIVE_PHASE_UNOBSERVABLE", "xx": "RELATIVE_PHASE_DISTINGUISHABLE",
            "claim": "Identical Z probabilities do not establish equal states; XX parity separates these orthogonal states."},
        "measurement_ids": m.collect(phase, [("bell_plus", plus), ("bell_minus", minus)], ("ZZ", "XX"))})

    broken = Circuit(n_qubits=2, gates=(Gate(name="x", qubits=(0,)),))
    repairs = [("remove_x", Circuit(n_qubits=2, gates=()), {"operator": "remove", "index": 0}),
               ("replace_x_by_z", Circuit(n_qubits=2, gates=(Gate(name="z", qubits=(0,)),)),
                {"operator": "replace", "index": 0, "after": "z"}),
               ("insert_x", Circuit(n_qubits=2, gates=broken.gates + (Gate(name="x", qubits=(0,)),)),
                {"operator": "insert", "index": 1, "after": "x"})]
    repair_states = [density(c) for _, c, _ in repairs]
    distances = [float(np.linalg.norm(a.data - b.data)) for a, b in combinations(repair_states, 2)]
    settings = ("ZZ", "XX", "YY")
    equivalence = "equivalent_repairs"
    repair_ids = m.collect(equivalence, [(name, c) for name, c, _ in repairs], settings)
    examples.append({"example_id": equivalence, "declared_input": "00", "submitted_circuit": broken.model_dump(mode="json"),
        "subjects": [subject(name, c, edit=edit) for name, c, edit in repairs],
        "evaluator_oracle": {"label": "PRIVILEGED_EXACT_FIXED_INPUT_STATES_AND_UNITARIES",
            "maximum_pairwise_density_distance": max(distances),
            "some_full_unitaries_differ": not Operator(repairs[0][1].native()).equiv(Operator(repairs[1][1].native())),
            "common_state": "|00><00|", "selected_povm_distributions": {s: probabilities(repair_states[0], s) for s in settings}},
        "identifiability": {"all_povms_indistinguishable_on_declared_input": True,
            "causal_origin": "NOT_IDENTIFIABLE_FROM_FIXED_INPUT_OUTPUT",
            "claim": "Distinct one-edit programs produce exactly the same output density. No measurement on that fixed-input output distinguishes them."},
        "measurement_ids": repair_ids})

    logical_rho, channel_rho = density(broken), explicit_channel_density()
    channel = "logical_vs_channel"
    examples.append({"example_id": channel, "subjects": [subject("logical_x", broken),
            {"name": "physical_bit_flip", "preparation": "00", "circuit_before_channel": Circuit(n_qubits=2, gates=()).model_dump(mode="json")}],
        "channel": {"definition": "E(rho) = X_0 rho X_0", "kraus_operators": [[[0., 1.], [1., 0.]]],
                    "supported_by_qfault_noise_schema": False,
                    "scope": "Explicit Qiskit executor demonstration only; not a newly supported QFAULT noise option"},
        "evaluator_oracle": {"label": "PRIVILEGED_EXACT_STATE_AND_CHANNEL_EVOLUTION",
            "density_distance": float(np.linalg.norm(logical_rho.data - channel_rho.data)),
            "common_state": "|01><01|", "selected_povm_distributions": {s: probabilities(channel_rho, s) for s in settings}},
        "identifiability": {"causal_origin": "NOT_IDENTIFIABLE_FROM_OUTPUT_STATE",
            "all_povms_indistinguishable": True,
            "claim": "A logical X and a deterministic physical bit-flip channel implement the same map. Output measurements cannot identify their causal origin without extra assumptions or controls."},
        "measurement_ids": m.collect(channel, [("logical_x", broken), ("physical_bit_flip", None)], settings,
                                     channel_subject="physical_bit_flip")})

    examples.append({"example_id": "more_shots_unchanged", "references_example": equivalence,
        "shot_grid": list(shot_grid), "ambiguity_at_each_shot_count": [len(repairs)] * len(shot_grid),
        "exact_product_distributions_equal_for_any_shot_count": True,
        "basis_of_conclusion": "Equal density matrices imply identical POVM probabilities; tensor powers preserve equality",
        "interpretation": "More shots shrink sampling uncertainty. They cannot separate identical fixed-input output states or identify which repair caused them.",
        "measurement_ids": repair_ids})

    superposition = Circuit(n_qubits=2, gates=(Gate(name="h", qubits=(0,)), Gate(name="h", qubits=(1,))))
    zero = Circuit(n_qubits=2, gates=())
    rp = density(superposition)
    readout_effective = DensityMatrix(np.eye(4) / 4)
    readout = "readout_z_ambiguity"
    examples.append({"example_id": readout, "subjects": [subject("logical_superposition", superposition), subject("zero_with_readout", zero)],
        "noise_configuration": Noise(readout=.5).model_dump(),
        "evaluator_oracle": {"label": "PRIVILEGED_EXACT_DISTRIBUTIONS_AND_KNOWN_READOUT_CHANNEL",
            "z_total_variation": tv(probabilities(rp, "ZZ"), probabilities(readout_effective, "ZZ")),
            "xx_total_variation": tv(probabilities(rp, "XX"), probabilities(readout_effective, "XX")),
            "readout_effective_state": "I/4; valid for independent symmetric p=0.5 readout and noiseless analysis gates"},
        "identifiability": {"z_only_causal_attribution": "NOT_ESTABLISHED", "xx": "DISTINGUISHABLE",
            "claim": "A logical uniform superposition and readout-randomized zero preparation have identical Z probabilities; additional calibrated bases distinguish this pair."},
        "measurement_ids": m.collect(readout, [("logical_superposition", superposition), ("zero_with_readout", zero)],
                                     ("ZZ", "XX"), noise_by_subject={"zero_with_readout": Noise(readout=.5)})})

    after = source_hashes()
    if before != after:
        raise RuntimeError("Source changed during identifiability demonstration")
    versions = {package: version(package) for package in ("qiskit", "numpy", "scipy", "pydantic")}
    if "aer" in backends:
        versions["qiskit-aer"] = version("qiskit-aer")
    records = m.records
    report = {"schema_version": 1, "kind": "identifiability_counterexamples", "version": "identifiability-v1",
        "purpose": "Reproducible explicit examples; not an untouched holdout or a causal-attribution success score",
        "settings": {"shot_grid": list(shot_grid), "seed": seed, "backends": list(backends),
            "seed_rule": "(seed + 7919 * execution_index) modulo 2^32; distinct seeds, no matched-count inference"},
        "software_versions": {"python": platform.python_version(), **versions},
        "provenance": {"source_sha256": before, "canonicalization": "qfault-json-v1"},
        "examples": examples, "measurements": records,
        "cost": {"executions": len(records), "shots": sum(r["shots"] for r in records),
                 "by_backend": {b: {"executions": sum(r["backend"] == b for r in records),
                     "shots": sum(r["shots"] for r in records if r["backend"] == b)} for b in backends},
                 "analysis_gate_and_channel_depth_sum": sum(r["resources"]["depth"] for r in records),
                 "scope": "Sampled executions and shots include each measurement once; example references do not duplicate cost"},
        "limitations": ["Local simulated data, not hardware validation", "Exact oracles are evaluator-side demonstrations, not analyst features",
            "Finite sampled histograms need not match when exact distributions match", "Identical density matrices imply identical probabilities for every POVM, independently of shots",
            "The explicit deterministic bit-flip channel is not supported by the QFAULT Noise schema",
            "No calibrated class probability, generalization result, or population error rate is inferred"]}
    report["report_digest"] = digest(report)
    return report


def write_report(path, report):
    """Exclusive output: never replace a frozen artifact."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(canonical(report))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--shots", type=int, nargs="+", default=[256, 4096])
    parser.add_argument("--seed", type=int, default=20261016)
    parser.add_argument("--backends", choices=("reference", "aer"), nargs="+", default=["reference", "aer"])
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    report = build_report(tuple(args.shots), args.seed, tuple(args.backends))
    write_report(args.out, report)
    print(f"{args.out}: {len(report['examples'])} examples, {report['cost']['executions']} executions, {report['cost']['shots']} shots")


if __name__ == "__main__":
    main()
