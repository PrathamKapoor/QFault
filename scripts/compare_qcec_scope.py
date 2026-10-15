"""Optional full-reference oracle illustration; no QFAULT performance comparison.

Install the isolated, pinned comparator using docs/competitor-comparison.md.
Output creation is exclusive so frozen evidence cannot be overwritten by accident.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def run() -> dict:
    try:
        import numpy as np
        from mqt import qcec
        from qiskit import QuantumCircuit, qasm2
        from qiskit.quantum_info import Statevector
    except ImportError as exc:
        raise SystemExit(
            "Optional comparator missing: install the pinned isolated environment "
            "from docs/competitor-comparison.md."
        ) from exc

    if version("mqt.qcec") != "3.11.0":
        raise SystemExit("This frozen protocol requires mqt.qcec==3.11.0; see the isolated install command.")

    reference = QuantumCircuit(2)
    reference.h(0)
    reference.cx(0, 1)
    equivalent = reference.copy()
    equivalent.x(1)
    equivalent.x(1)
    removed = QuantumCircuit(2)
    removed.h(0)
    phase = reference.copy()
    phase.z(0)
    same_zero_state = QuantumCircuit(2)
    same_zero_state.z(0)
    same_zero_state.compose(reference, inplace=True)
    candidates = (
        ("identity_pair_inserted", equivalent, "equivalent"),
        ("cx_removed", removed, "not_equivalent"),
        ("relative_phase_z_appended", phase, "not_equivalent"),
        ("initial_z_invisible_on_zero_input", same_zero_state, "not_equivalent"),
    )
    options = {"method": "construction", "parallel": False, "timeout": 5}
    reference_qasm = qasm2.dumps(reference)
    reference_state = Statevector.from_instruction(reference)
    cases = []
    for name, candidate, expected in candidates:
        raw = json.loads(str(qcec.verify(reference, candidate, **options)))
        verdict = raw["equivalence"]
        if verdict != expected:
            raise RuntimeError(f"{name}: expected {expected}, received {verdict}")
        state = Statevector.from_instruction(candidate)
        qasm = qasm2.dumps(candidate)
        cases.append({
            "case": name,
            "candidate_qasm2": qasm,
            "candidate_sha256": digest(qasm.encode("utf-8")),
            "expected_equivalence": expected,
            "equivalence": verdict,
            "checker_verdicts": [
                {"checker": checker["checker"], "equivalence": checker["equivalence"]}
                for checker in raw.get("checkers", [])
            ],
            "zero_input_z_distribution_equal": bool(np.allclose(
                reference_state.probabilities(), state.probabilities(), atol=1e-12, rtol=0)),
            "zero_input_state_fidelity": float(abs(np.vdot(reference_state.data, state.data)) ** 2),
        })
    report = {
        "schema_version": 1,
        "task": "two-qubit full-reference unitary equivalence scope demonstration",
        "oracle_scope": {
            "qcec_access": "complete trusted reference and candidate circuit descriptions",
            "equivalence_relation": "full-unitary equivalence up to global phase",
            "comparison_to_qfault": "stronger oracle; not an equal-information performance or repair comparison",
            "interpretation_access": "privileged exact Statevector for zero input; no measured QFAULT run",
            "shots": 0,
            "fault_localization_or_repair_evaluated": False,
        },
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "packages": {name: version(name) for name in (
                "mqt.qcec", "mqt.core", "qiskit", "numpy", "scipy", "rustworkx",
                "dill", "stevedore", "typing-extensions", "nanobind-backend")},
        },
        "source": {
            "script_path": "scripts/compare_qcec_scope.py",
            "script_sha256": digest(Path(__file__).read_bytes()),
            "qcec_release": "3.11.0",
            "qcec_release_source_commit": "844a67c94159ae97d1c4cc01501fbdd98a84a730",
        },
        "checker_options": options,
        "reference_qasm2": reference_qasm,
        "reference_sha256": digest(reference_qasm.encode("utf-8")),
        "cases": cases,
        "expected_verdicts_matched": len(cases),
        "digest_definition": "SHA-256 of UTF-8 JSON with sort_keys=True and separators=(',',':'), excluding payload_sha256",
    }
    report["payload_sha256"] = digest(json.dumps(
        report, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New JSON output path; existing files are rejected")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists; choose a new path to preserve frozen evidence")
    report = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(report, indent=2) + "\n")
    print(f"{report['expected_verdicts_matched']}/4 expected verdicts matched; payload SHA-256 {report['payload_sha256']}")


if __name__ == "__main__":
    main()
