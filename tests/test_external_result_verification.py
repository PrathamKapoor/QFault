"""Independent external-result verification catches rehashed reporting mistakes."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from qfault.evidence import canonical, digest
from qfault.counterfactual import RecoveryRequest, recover
from qfault.lab import LabRequest, investigate_lab
from qfault.storage import ArtifactStore


def verifier():
    import scripts
    assert (Path(scripts.__file__).parent / "verify_external_results.py").exists(), "independent result verifier missing"
    from scripts.verify_external_results import verify_results
    return verify_results


@pytest.fixture
def evidence(tmp_path):
    result = investigate_lab(LabRequest.model_validate({
        "circuit": {"schema_version": 1, "name": "audit fixture", "n_qubits": 2,
            "input": {"kind": "computational_basis", "bitstring": "00"},
            "gates": [{"name": "h", "qubits": [0]}, {"name": "cx", "qubits": [0, 1]}]},
        "contract": {"kind": "pauli_expectations", "observables": [{"pauli": "ZZ", "expected": 1., "tolerance": .2}]},
        "diagnostic_mode": "measurement_only", "backend": "reference", "policy": "fixed", "seed": 17,
        "batch_shots": 64, "max_shots": 128, "max_evaluations": 2, "max_looks": 1}))
    result["evaluation_truth"] = {"source_path": "small/fixture_n2/fixture_n2.qasm", "variant": "clean",
                                  "contract_violated": False, "exact_loss": 0.}
    store = ArtifactStore(tmp_path / "store")
    eid = store.save(result)
    report = store.export(eid)
    row = {"experiment_id": eid, "source_path": result["evaluation_truth"]["source_path"], "variant": "clean",
           "kind": "pauli_expectations", "policy": "fixed", "seed": 17, "error": None,
           "manifest_digest": digest(report["manifest"]), "category": result["diagnosis"]["category"],
           "contract_violated": False, "shots": result["cost"]["shots"], "evaluations": result["cost"]["evaluations"]}
    summary = {"rows": [row], "recovery_rows": [], "architecture_count": 1,
        "summaries": {"pauli_expectations/fixed": {"runs": 1, "architectures": 1,
            "observable_violations": 0, "detected_violations": 0, "missed_or_unresolved_violations": 0,
            "oracle_nonviolations": 1, "false_alarms": 0,
            "total_shots": row["shots"], "total_executions": row["evaluations"]}},
        "recovery_summaries": {}}
    return tmp_path, summary, [report]


def save(evidence, *, rehash=True):
    folder, summary, reports = evidence
    archive = folder / "reports.jsonl.gz"
    with gzip.open(archive, "wb") as stream:
        for report in reports:
            stream.write(canonical(report) + b"\n")
    summary["raw_exports"] = {"file": archive.name, "count": len(reports),
                              "sha256": hashlib.sha256(archive.read_bytes()).hexdigest()}
    if rehash:
        summary.pop("digest", None)
        summary["digest"] = digest(summary)
    path = folder / "summary.json"
    path.write_bytes(canonical(summary))
    return path, archive


def test_real_export_and_independently_counted_summary_verify(evidence):
    paths = save(evidence)
    result = verifier()(*paths)
    assert result["valid"] is True, result["errors"]
    assert result["counts"]["reports"] == 1
    assert result["counts"]["diagnostic_rows"] == 1


@pytest.mark.parametrize("change", ["shots", "category", "manifest_digest", "source_path", "contract_violated"])
def test_rehashed_summary_cannot_disagree_with_stored_report(evidence, change):
    row = evidence[1]["rows"][0]
    row[change] = {"shots": row["shots"] + 1, "category": "SIGNIFICANT_DISCREPANCY",
                   "manifest_digest": "0" * 64, "source_path": "changed.qasm", "contract_violated": True}[change]
    result = verifier()(*save(evidence))
    assert result["valid"] is False
    assert any(change in error for error in result["errors"])


def test_rehashed_aggregate_cannot_invent_detection_counts(evidence):
    evidence[1]["summaries"]["pauli_expectations/fixed"]["detected_violations"] = 1
    result = verifier()(*save(evidence))
    assert not result["valid"]
    assert any("detected_violations" in error for error in result["errors"])


def test_invalid_summary_digest_is_rejected(evidence):
    evidence[1]["digest"] = "0" * 64
    result = verifier()(*save(evidence, rehash=False))
    assert not result["valid"]
    assert any("summary digest" in error for error in result["errors"])


def test_duplicate_archive_experiments_are_rejected_even_with_rehashed_archive(evidence):
    evidence[2].append(copy.deepcopy(evidence[2][0]))
    result = verifier()(*save(evidence))
    assert not result["valid"]
    assert any("duplicate experiment" in error for error in result["errors"])


def test_summary_row_and_export_membership_must_match_exactly(evidence):
    evidence[1]["rows"] = []
    result = verifier()(*save(evidence))
    assert not result["valid"]
    assert any("unmatched export" in error for error in result["errors"])


def test_modified_export_is_rejected_even_with_new_archive_and_summary_hash(evidence):
    evidence[2][0]["investigation"]["cost"]["shots"] += 1
    result = verifier()(*save(evidence))
    assert not result["valid"]
    assert any("export integrity" in error for error in result["errors"])


def test_archive_hash_is_checked_without_trusting_export_hashes(evidence):
    paths = save(evidence)
    evidence[1]["raw_exports"]["sha256"] = "0" * 64
    summary = evidence[1]
    summary.pop("digest")
    summary["digest"] = digest(summary)
    paths[0].write_bytes(canonical(summary))
    result = verifier()(*paths)
    assert not result["valid"]
    assert any("archive SHA256" in error for error in result["errors"])


@pytest.mark.parametrize("change", [None, "status", "cost"])
def test_real_recovery_exports_are_matched_and_checked(evidence, change):
    original = evidence[2][0]["investigation"]["configuration"]
    result = recover(RecoveryRequest.model_validate({"circuit": original["circuit"],
        "contract": original["contract"], "backend": "reference", "seed": 29,
        "selection_policy": "no_repair", "screen_shots": 64, "verification_shots": 64,
        "max_shots": 512, "max_evaluations": 8, "max_candidates": 1}))
    result["evaluation_truth"] = {"source_path": "small/fixture_n2/fixture_n2.qasm", "variant": "clean", "truth_locus": None}
    store = ArtifactStore(evidence[0] / "recovery-store")
    report = store.export(store.save(result))
    row = {"source_path": result["evaluation_truth"]["source_path"], "variant": "clean", "truth_locus": None,
        "experiment_id": result["experiment_id"], "manifest_digest": digest(report["manifest"]),
        "status": result["status"], "policy": "no_repair", "seed": 29, "error": None,
        "eligible": False, "selected": False, "cost": {"shots": result["cost"]["shots"], "evaluations": result["cost"]["evaluations"]}}
    evidence[1]["recovery_rows"] = [row]
    evidence[1]["recovery_summaries"] = {"no_repair": {"runs": 1, "architectures": 1, "eligible": 0,
        "selected": 0, "outcomes": {result["status"]: 1}, "shots": row["cost"]["shots"], "executions": row["cost"]["evaluations"]}}
    evidence[2].append(report)
    if change == "status":
        row["status"] = "VERIFIED_UNDER_DECLARED_CONTRACT"
    elif change == "cost":
        row["cost"]["shots"] += 1
    audited = verifier()(*save(evidence))
    assert audited["valid"] is (change is None), audited["errors"]
    if change:
        assert any(change in error for error in audited["errors"])


def test_streamed_report_line_size_is_bounded(evidence, monkeypatch):
    from scripts import verify_external_results as audit
    monkeypatch.setattr(audit, "MAX_LINE_BYTES", 128)
    result = audit.verify_results(*save(evidence))
    assert not result["valid"]
    assert any("line" in error and "limit" in error for error in result["errors"])


def test_cli_returns_failure_for_invalid_summary_digest(evidence):
    evidence[1]["digest"] = "0" * 64
    summary_path, archive = save(evidence, rehash=False)
    command = subprocess.run([sys.executable, "-m", "scripts.verify_external_results", str(summary_path), str(archive)],
                             capture_output=True, text=True, check=False)
    assert command.returncode == 1
    assert json.loads(command.stdout)["valid"] is False


def test_raw_export_count_cannot_disagree_with_actual_archive(evidence):
    paths = save(evidence)
    summary = evidence[1]
    summary["raw_exports"]["count"] = 2
    summary.pop("digest")
    summary["digest"] = digest(summary)
    paths[0].write_bytes(canonical(summary))
    result = verifier()(*paths)
    assert not result["valid"]
    assert any("raw_exports.count" in error for error in result["errors"])


def test_missing_export_is_rejected_even_with_new_archive_hash(evidence):
    evidence[2].clear()
    result = verifier()(*save(evidence))
    assert not result["valid"]
    assert any("missing export" in error for error in result["errors"])
