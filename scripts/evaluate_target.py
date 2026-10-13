"""Matched-budget comparison of target-state witness policies (measurement-only).

Usage: python scripts/evaluate_target.py --split development|holdout --out benchmarks/<name>.json [--backend reference|aer]
Protocol (cases, seeds, budgets, policies, metrics) is frozen in configs/target-witness-protocol.json.
"""
import argparse
import json
import platform
import sys
from math import sqrt
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qfault.lab import LabRequest, investigate_lab
from qfault.target_corpus import BUDGETS, SPLITS, cases, truth
from qfault.target import POLICY_VERSION, CATALOG_VERSION
from qfault.evidence import canonical, digest

POLICIES = ["fixed", "random", "complementary_schedule", "coefficient_weighted", "adaptive_witness"]


def wilson(k, n, z=1.96):
    if not n:
        return None
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0, c - h), 4), round(min(1, c + h), 4)]


def run(split, backend):
    rows = []
    for case in cases(split):
        t = truth(case)
        for policy in POLICIES:
            r = investigate_lab(LabRequest.model_validate({
                "circuit": case["circuit"], "contract": case["contract"], "diagnostic_mode": "measurement_only",
                "policy": policy, "backend": backend, "environment": case["environment_noise"], "seed": case["seed"],
                **BUDGETS[case["budget"]]}))
            ev = r["target_evidence"]
            L, U = ev["fidelity_bound"]
            eff = t["effective_fidelity"]
            rows.append({"case_id": case["case_id"], "policy": policy, "family": case["family"], "budget": case["budget"],
                         "truth_class": t["class"], "ideal_fidelity": t["ideal_fidelity"], "effective_fidelity": eff,
                         "effective_violation": t["effective_violation"], "stabilizer_target": t["stabilizer_target"],
                         "catalog_terms": t["catalog_terms"], "category": r["diagnosis"]["category"],
                         "stop": r["diagnosis"]["stop"]["code"], "lower": L, "upper": U, "width": U - L,
                         "covered": None if eff is None else (L - 1e-9 <= eff <= U + 1e-9),
                         "terms_measured": ev["terms_measured"], "witness_discrepancies": len(ev["witness_discrepancies"]),
                         "settings": [a["measurement_specification"]["setting"] for a in r["action_ledger"]],
                         "shots": r["cost"]["shots"], "evaluations": r["cost"]["evaluations"],
                         "basis_gates": r["cost"]["basis_gates"], "runtime_seconds": r["cost"]["runtime_seconds"],
                         "max_shots": BUDGETS[case["budget"]]["max_shots"]})
    return rows


def summarize(rows):
    out = {}
    for budget in BUDGETS:
        for p in POLICIES:
            sub = [r for r in rows if r["policy"] == p and r["budget"] == budget]
            cls = lambda c: [r for r in sub if r["truth_class"] == c]
            viol, clean, noise = cls("logical_violation"), cls("clean_correct"), cls("noise_only")
            det = lambda rs: sum(r["category"] == "SIGNIFICANT_DISCREPANCY" for r in rs)
            conf = lambda rs: sum(r["category"] == "NO_SIGNIFICANT_DISCREPANCY" for r in rs)
            cov = [r["covered"] for r in sub if r["covered"] is not None]
            out[f"{budget}/{p}"] = {
                "cases": len(sub),
                "detection": {"logical_violations": len(viol), "detected": det(viol), "wilson95": wilson(det(viol), len(viol)),
                              "insufficient": sum(r["category"] == "INSUFFICIENT_EVIDENCE" for r in viol)},
                "clean_correct": {"n": len(clean), "false_alarms": det(clean), "confirmed": conf(clean),
                                  "insufficient": len(clean) - det(clean) - conf(clean), "confirmed_wilson95": wilson(conf(clean), len(clean))},
                "noise_only": {"n": len(noise), "flagged": det(noise), "confirmed": conf(noise)},
                "bound": {"coverage": [sum(cov), len(cov)], "mean_width": float(np.mean([r["width"] for r in sub])),
                          "median_width": float(np.median([r["width"] for r in sub]))},
                "mean_shots": float(np.mean([r["shots"] for r in sub])), "mean_evaluations": float(np.mean([r["evaluations"] for r in sub])),
                "mean_basis_gates": float(np.mean([r["basis_gates"] for r in sub])),
                "budget_fraction": float(np.mean([r["shots"] / r["max_shots"] for r in sub])),
                "early_stop_fraction": float(np.mean([r["stop"] == "ALL_CLAIMS_RESOLVED" for r in sub])),
                "runtime_seconds": float(sum(r["runtime_seconds"] for r in sub))}
    rng = np.random.default_rng(20261013)
    paired = {}
    for budget in BUDGETS:
        a = {r["case_id"]: r for r in rows if r["policy"] == "adaptive_witness" and r["budget"] == budget}
        for p in POLICIES[:-1]:
            b = {r["case_id"]: r for r in rows if r["policy"] == p and r["budget"] == budget}
            ids = sorted(a)
            diff = np.array([b[i]["shots"] - a[i]["shots"] for i in ids], float)
            wdiff = np.array([b[i]["width"] - a[i]["width"] for i in ids], float)
            boot = lambda x: [float(np.percentile([rng.choice(x, len(x)).mean() for _ in range(2000)], q)) for q in (2.5, 97.5)]
            decisive = lambda r: r["category"] != "INSUFFICIENT_EVIDENCE"
            paired[f"{budget}/{p}_minus_adaptive"] = {
                "n": len(ids), "shots_mean": float(diff.mean()), "shots_bootstrap95": boot(diff),
                "adaptive_cheaper": int((diff > 0).sum()), "adaptive_costlier": int((diff < 0).sum()), "ties": int((diff == 0).sum()),
                "width_mean": float(wdiff.mean()), "width_bootstrap95": boot(wdiff),
                "decisive_only_adaptive": sum(decisive(a[i]) and not decisive(b[i]) for i in ids),
                "decisive_only_baseline": sum(decisive(b[i]) and not decisive(a[i]) for i in ids),
                "category_agreement": [sum(a[i]["category"] == b[i]["category"] for i in ids), len(ids)],
                "action_order_differs": sum(a[i]["settings"] != b[i]["settings"] for i in ids)}
    return out, paired


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=list(SPLITS), required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--backend", choices=["reference", "aer"], default="reference")
    a = ap.parse_args()
    rows = run(a.split, a.backend)
    summary, paired = summarize(rows)
    import qiskit
    result = {"split": a.split, "backend": a.backend, "budgets": BUDGETS, "policies": POLICIES,
              "policy_version": POLICY_VERSION, "catalog_version": CATALOG_VERSION,
              "mode": "measurement_only (no privileged state access)", "case_count": len(rows) // len(POLICIES),
              "spec": SPLITS[a.split], "software": {"qiskit": qiskit.__version__, "python": platform.python_version()},
              "summary": summary, "paired_vs_adaptive_witness": paired, "rows": rows,
              "notes": ["Truth labels are evaluator-side; policies never see them.",
                        "logical_violation = candidate's ideal fidelity below 1 - tolerance.",
                        "Coverage is defined only without gate noise (readout maps exactly to a local depolarizing state channel).",
                        "Cases share circuits across seeds and budgets; Wilson/bootstrap intervals are descriptive and optimistic."]}
    result["digest"] = digest({k: v for k, v in result.items() if k != "digest"})
    Path(a.out).write_bytes(canonical(result))
    print(json.dumps({"out": a.out, "cases": result["case_count"], "summary": summary, "paired": paired}, indent=1))


if __name__ == "__main__":
    main()
