"""Independently audit external-result summaries against their exported evidence.

This checks unsigned artifact consistency and independently counts reporting
denominators. It does not rerun experiments or prove the reference specification.
The evaluator and its summarize function are deliberately not imported.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import zlib

from qfault.evidence import digest
from qfault.storage import verify_export

MAX_LINE_BYTES = 16 * 1024 * 1024
MAX_SUMMARY_BYTES = 64 * 1024 * 1024


def _file_sha256(path):
    hasher = hashlib.sha256()
    with Path(path).open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest()


def _matches(actual, expected, label, errors):
    if actual != expected:
        # Artifact payloads may be large; point at the failing field without
        # reproducing whole investigation or architecture dictionaries.
        recorded = repr(actual)
        reconstructed = repr(expected)
        if len(recorded) > 180:
            recorded = recorded[:177] + "..."
        if len(reconstructed) > 180:
            reconstructed = reconstructed[:177] + "..."
        errors.append(f"{label} mismatch: recorded {recorded}, reconstructed {reconstructed}")


def _diagnostic_counts(rows):
    groups = {}
    for row in rows:
        key = row["kind"] + "/" + row["policy"]
        groups.setdefault(key, []).append(row)
    counted = {}
    for key, group in groups.items():
        values = {"runs": 0, "architectures": 0, "observable_violations": 0,
                  "detected_violations": 0, "missed_or_unresolved_violations": 0,
                  "oracle_nonviolations": 0, "false_alarms": 0, "unresolved": 0,
                  "uncheckable_model": 0, "total_shots": 0, "total_executions": 0,
                  "runtime_seconds": 0, "outcomes": Counter(), "attribution": Counter(),
                  "by_architecture": {}}
        for row in group:
            values["runs"] += 1
            values["outcomes"][row["category"]] += 1
            values["total_shots"] += row.get("shots", 0)
            values["total_executions"] += row.get("evaluations", 0)
            values["runtime_seconds"] += row.get("runtime_seconds", 0)
            architecture = values["by_architecture"].setdefault(row["source_path"], {
                "runs": 0, "observable_violations": 0, "detected_violations": 0,
                "false_alarms": 0, "outcomes": Counter(), "shots": 0})
            architecture["runs"] += 1
            architecture["outcomes"][row["category"]] += 1
            architecture["shots"] += row.get("shots", 0)
            positive = row.get("contract_violated") is True
            discrepancy = row["category"] == "SIGNIFICANT_DISCREPANCY"
            if positive:
                architecture["observable_violations"] += 1
                architecture["detected_violations"] += int(discrepancy)
            elif row.get("contract_violated") is False:
                architecture["false_alarms"] += int(discrepancy)
            if row.get("error") or row["category"] in {"UNSUPPORTED", "ERROR"}:
                continue
            values["attribution"][row.get("attribution", "NOT_APPLICABLE")] += 1
            values["unresolved"] += int(row["category"] == "INSUFFICIENT_EVIDENCE")
            if positive:
                values["observable_violations"] += 1
                values["detected_violations"] += int(discrepancy)
                values["missed_or_unresolved_violations"] += int(not discrepancy)
            elif row.get("contract_violated") is False:
                values["oracle_nonviolations"] += 1
                values["false_alarms"] += int(discrepancy)
            else:
                values["uncheckable_model"] += 1
        values["architectures"] = len(values["by_architecture"])
        counted[key] = values
    return counted


def _recovery_counts(rows):
    groups = {}
    for row in rows:
        groups.setdefault(row["policy"], []).append(row)
    counted = {}
    for policy, group in groups.items():
        values = {"runs": len(group), "architectures": len({r["source_path"] for r in group}),
                  "eligible": 0, "selected": 0, "outcomes": Counter(), "noise_only_proposals": 0,
                  "generated_candidates": 0, "tested_candidates": 0, "shots": 0, "executions": 0,
                  "searched_truth_cases": 0, "true_locus_covered": 0}
        for row in group:
            values["outcomes"][row["status"]] += 1
            values["eligible"] += int(bool(row.get("eligible")))
            selected = bool(row.get("selected"))
            values["selected"] += int(selected)
            values["noise_only_proposals"] += int(selected and row["variant"] in {"readout", "gate_noise"})
            values["searched_truth_cases"] += int(bool(row.get("plausible_loci")) and row.get("truth_locus") is not None)
            values["true_locus_covered"] += int(row.get("true_locus_covered") is True)
            cost = row.get("cost", {})
            for field in ("generated_candidates", "tested_candidates", "shots"):
                values[field] += cost.get(field, 0)
            values["executions"] += cost.get("evaluations", 0)
        counted[policy] = values
    return counted


def _compare_aggregates(recorded, counted, label, errors):
    if not isinstance(recorded, dict):
        errors.append(label + " must be an object")
        return
    if set(recorded) != set(counted):
        errors.append(label + " policy/contract membership mismatch")
    for key in recorded.keys() & counted.keys():
        group = recorded[key]
        if not isinstance(group, dict):
            errors.append(f"{label}.{key} must be an object")
            continue
        # Optional detailed metrics are all checked when present. Core reporting
        # denominators are mandatory even for a compact summary.
        required = ({"runs", "architectures", "observable_violations", "detected_violations",
                     "missed_or_unresolved_violations", "oracle_nonviolations", "false_alarms",
                     "total_shots", "total_executions"} if label == "summaries" else
                    {"runs", "architectures", "eligible", "selected", "outcomes", "shots", "executions"})
        for missing in sorted(required - group.keys()):
            errors.append(f"{label}.{key}.{missing} missing")
        for field, value in group.items():
            if field not in counted[key]:
                errors.append(f"{label}.{key}.{field} is not an audited metric")
            else:
                _matches(value, counted[key][field], f"{label}.{key}.{field}", errors)


def _check_report_row(report, row, kind, errors):
    investigation, evaluation = report["investigation"], report["evaluation"]
    eid = investigation["experiment_id"]
    label = kind + " row " + eid
    _matches(row["manifest_digest"], digest(report["manifest"]), label + ".manifest_digest", errors)
    for field in ("source_path", "variant"):
        _matches(row[field], evaluation.get(field), label + "." + field, errors)
    configuration = investigation["configuration"]
    if "seed" in row:
        _matches(row["seed"], configuration.get("seed"), label + ".seed", errors)
    cost = investigation["cost"]
    if kind == "diagnostic":
        _matches(investigation.get("investigation_kind"), "custom_circuit", label + ".investigation_kind", errors)
        for field, actual in {"category": investigation["diagnosis"]["category"],
                              "kind": configuration["contract"]["kind"], "policy": configuration["policy"],
                              "shots": cost["shots"], "evaluations": cost["evaluations"],
                              "contract_violated": evaluation.get("contract_violated")}.items():
            _matches(row.get(field), actual, label + "." + field, errors)
        optional = {"exact_loss": evaluation.get("exact_loss"),
                    "attribution": investigation["diagnosis"]["attribution"]["status"],
                    "runtime_seconds": cost["runtime_seconds"], "basis_gates": cost["basis_gates"],
                    "resource_actions": cost["actions"]}
        target = investigation.get("target_evidence")
        optional["fidelity_interval"] = target["fidelity_bound"] if target else None
        for field, actual in optional.items():
            if field in row:
                _matches(row[field], actual, label + "." + field, errors)
    else:
        _matches(investigation.get("investigation_kind"), "counterfactual_recovery", label + ".investigation_kind", errors)
        _matches(row["status"], investigation["status"], label + ".status", errors)
        _matches(row["policy"], configuration["selection_policy"], label + ".policy", errors)
        for field in ("shots", "evaluations"):
            _matches(row["cost"][field], cost[field], label + ".cost." + field, errors)
        for field, value in row["cost"].items():
            _matches(value, cost.get(field), label + ".cost." + field, errors)
        original, control = investigation["original_evidence"], investigation["readout_control"]
        loci = investigation["localization"]["plausible_loci"]
        truth_locus = evaluation.get("truth_locus")
        optional = {"verification_status": investigation["verification"]["status"],
                    "detected": bool(original and original["loss_interval"][0] > 1),
                    "eligible": bool(original and original["loss_interval"][0] > 1 and control and not control["significant"]),
                    "selected": bool(investigation["selected_candidate"]), "plausible_loci": loci,
                    "true_locus_covered": truth_locus in loci if truth_locus is not None else None,
                    "truth_locus": truth_locus,
                    "plausible_candidates": sum(bool(c["plausible"]) for c in investigation["ranked_candidates"]),
                    "causal_origin": investigation["localization"]["causal_origin"]}
        for field, actual in optional.items():
            if field in row:
                _matches(row[field], actual, label + "." + field, errors)


def verify_results(summary_path, reports_path=None):
    """Return validity, independently checked counts and actionable errors."""
    errors = []
    counts = {"reports": 0, "diagnostic_rows": 0, "recovery_rows": 0, "expected_exports": 0}
    result = {"valid": False, "counts": counts, "errors": errors,
              "assurance": "Unsigned digest, membership, report/row and aggregate consistency; no scientific correctness proof"}
    try:
        summary_path = Path(summary_path)
        with summary_path.open("rb") as stream:
            raw = stream.read(MAX_SUMMARY_BYTES + 1)
        if len(raw) > MAX_SUMMARY_BYTES:
            raise ValueError("summary exceeds size limit")
        summary = json.loads(raw)
        body = dict(summary)
        recorded_digest = body.pop("digest", None)
        _matches(recorded_digest, digest(body), "summary digest", errors)
        rows, recovery_rows = summary["rows"], summary["recovery_rows"]
        if not isinstance(rows, list) or not isinstance(recovery_rows, list):
            raise ValueError("summary rows must be arrays")
        counts.update(diagnostic_rows=len(rows), recovery_rows=len(recovery_rows))
        expected = {}
        for kind, group in (("diagnostic", rows), ("recovery", recovery_rows)):
            for row in group:
                status = row.get("category") if kind == "diagnostic" else row.get("status")
                if row.get("error") is not None or status in {"ERROR", "UNSUPPORTED"}:
                    continue
                eid = row["experiment_id"]
                if eid in expected:
                    errors.append("duplicate experiment in summary: " + eid)
                expected[eid] = (kind, row)
        counts["expected_exports"] = len(expected)
        archive_meta = summary["raw_exports"]
        if reports_path is None:
            filename = archive_meta["file"]
            if not isinstance(filename, str) or Path(filename).name != filename:
                raise ValueError("archive filename must be a local filename")
            reports_path = summary_path.parent / filename
        reports_path = Path(reports_path)
        _matches(archive_meta["sha256"], _file_sha256(reports_path), "archive SHA256", errors)
        seen = set()
        with gzip.open(reports_path, "rb") as archive:
            while line := archive.readline(MAX_LINE_BYTES + 1):
                counts["reports"] += 1
                if len(line) > MAX_LINE_BYTES:
                    errors.append(f"archive line {counts['reports']} exceeds 16 MiB limit")
                    break
                try:
                    report = json.loads(line)
                    verification = verify_export(report)
                    if not verification["valid"]:
                        errors.append(f"export integrity line {counts['reports']}: {verification['errors']}")
                    eid = report["investigation"]["experiment_id"]
                    if eid in seen:
                        errors.append("duplicate experiment in archive: " + eid)
                    seen.add(eid)
                    if eid not in expected:
                        errors.append("unmatched export: " + eid)
                    else:
                        kind, row = expected[eid]
                        _check_report_row(report, row, kind, errors)
                except (ValueError, TypeError, KeyError, AttributeError, RecursionError) as error:
                    errors.append(f"malformed export line {counts['reports']}: {type(error).__name__}: {error}")
        for missing in sorted(expected.keys() - seen):
            errors.append("missing export: " + missing)
        _matches(archive_meta["count"], counts["reports"], "raw_exports.count", errors)
        _matches(counts["reports"], len(expected), "row/export count", errors)
        _matches(summary.get("architecture_count"), len({r["source_path"] for r in rows}), "architecture_count", errors)
        _compare_aggregates(summary["summaries"], _diagnostic_counts(rows), "summaries", errors)
        _compare_aggregates(summary["recovery_summaries"], _recovery_counts(recovery_rows), "recovery_summaries", errors)
        if "failure_taxonomy" in summary:
            _matches(summary["failure_taxonomy"], dict(Counter(r["failure_taxonomy"] for r in rows)), "failure_taxonomy", errors)
    except (OSError, EOFError, ValueError, TypeError, KeyError, AttributeError, RecursionError, zlib.error) as error:
        errors.append(f"audit input failure: {type(error).__name__}: {error}")
    result["valid"] = not errors
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", type=Path)
    parser.add_argument("reports", nargs="?", type=Path)
    args = parser.parse_args()
    result = verify_results(args.summary, args.reports)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
