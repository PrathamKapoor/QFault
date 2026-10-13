"""Matched-budget policy comparison on prespecified custom-circuit cases (measurement-only).

Usage: python scripts/evaluate_lab.py --split development|holdout --out benchmarks/<name>.json [--backend reference|aer]
Policies and parameters are fixed in code before the holdout split is executed.
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
from qfault.lab_corpus import cases, truth, SPLITS
from qfault.evidence import canonical, digest

POLICIES = ["fixed", "random", "complementary_schedule", "adaptive"]
BUDGET = {"batch_shots": 1024, "max_shots": 10240, "max_evaluations": 24, "max_looks": 4, "alpha_total": 0.01}


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0, c - h), 4), round(min(1, c + h), 4)]


def run(split, backend, budget):
    rows = []
    for case in cases(split):
        t = truth(case)
        for policy in POLICIES:
            request = LabRequest.model_validate({
                "circuit": case["circuit"], "contract": case["contract"], "diagnostic_mode": "measurement_only",
                "policy": policy, "backend": backend, "environment": case["environment_noise"],
                "seed": case["seed"], **budget})
            r = investigate_lab(request)
            rows.append({"case_id": case["case_id"], "policy": policy, "truth_class": t["class"],
                         "family": case["family"], "category": r["diagnosis"]["category"],
                         "attribution": r["diagnosis"]["attribution"]["status"],
                         "stop": r["diagnosis"]["stop"]["code"], "shots": r["cost"]["shots"],
                         "evaluations": r["cost"]["evaluations"], "basis_gates": r["cost"]["basis_gates"],
                         "runtime_seconds": r["cost"]["runtime_seconds"],
                         "budget_exhausted": r["diagnosis"]["stop"]["code"] in {"SHOT_BUDGET_EXHAUSTED", "EVALUATION_BUDGET_EXHAUSTED", "LOOK_LIMIT_REACHED"},
                         "stopped_early": r["diagnosis"]["stop"]["code"] == "ALL_CLAIMS_RESOLVED" and r["cost"]["shots"] < budget["max_shots"]})
    return rows


def summarize(rows, budget):
    out = {}
    for p in POLICIES:
        sub = [r for r in rows if r["policy"] == p]
        by = lambda c: [r for r in sub if r["truth_class"] == c]
        fault, clean, noise = by("logical_fault"), by("clean_correct"), by("noise_only")
        det = lambda rs: sum(r["category"] == "SIGNIFICANT_DISCREPANCY" for r in rs)
        out[p] = {"cases": len(sub),
                  "logical_fault": {"n": len(fault), "detected": det(fault), "wilson95": wilson(det(fault), len(fault)),
                                    "insufficient": sum(r["category"] == "INSUFFICIENT_EVIDENCE" for r in fault)},
                  "clean_correct": {"n": len(clean), "false_alarms": det(clean), "wilson95": wilson(det(clean), len(clean)),
                                    "confirmed_no_discrepancy": sum(r["category"] == "NO_SIGNIFICANT_DISCREPANCY" for r in clean),
                                    "insufficient": sum(r["category"] == "INSUFFICIENT_EVIDENCE" for r in clean)},
                  "noise_only": {"n": len(noise), "flagged": det(noise), "wilson95": wilson(det(noise), len(noise))},
                  "attribution": {"unique_logical_claims": sum("LOGICAL_DEFECT" in r["attribution"] for r in sub),
                                  "ambiguous": sum(r["attribution"] == "AMBIGUOUS_LOGICAL_VS_NOISE" for r in sub),
                                  "noise_consistent": sum(r["attribution"] == "NOISE_CONSISTENT_NOT_UNIQUE" for r in sub)},
                  "mean_shots": float(np.mean([r["shots"] for r in sub])),
                  "total_shots": sum(r["shots"] for r in sub),
                  "mean_evaluations": float(np.mean([r["evaluations"] for r in sub])),
                  "mean_basis_gates": float(np.mean([r["basis_gates"] for r in sub])),
                  "total_runtime_seconds": sum(r["runtime_seconds"] for r in sub),
                  "fraction_budget_exhausted": float(np.mean([r["budget_exhausted"] for r in sub])),
                  "fraction_stopped_early": float(np.mean([r["stopped_early"] for r in sub]))}
    rng = np.random.default_rng(20261013)
    paired = {}
    for p in POLICIES[:-1]:
        a = {r["case_id"]: r for r in rows if r["policy"] == "adaptive"}
        b = {r["case_id"]: r for r in rows if r["policy"] == p}
        ids = sorted(a)
        diff = np.array([b[i]["shots"] - a[i]["shots"] for i in ids], float)
        boots = [rng.choice(diff, len(diff)).mean() for _ in range(2000)]
        same = sum(a[i]["category"] == b[i]["category"] for i in ids)
        paired[p + "_minus_adaptive_shots"] = {
            "mean": float(diff.mean()), "bootstrap95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
            "adaptive_cheaper": int((diff > 0).sum()), "adaptive_costlier": int((diff < 0).sum()), "ties": int((diff == 0).sum()),
            "category_agreement": [same, len(ids)]}
    return out, paired


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=list(SPLITS), required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--backend", choices=["reference", "aer"], default="reference")
    ap.add_argument("--max-shots", type=int, default=BUDGET["max_shots"])
    a = ap.parse_args()
    budget = {**BUDGET, "max_shots": a.max_shots}
    rows = run(a.split, a.backend, budget)
    summary, paired = summarize(rows, budget)
    import qiskit
    result = {"split": a.split, "backend": a.backend, "budget": budget, "policies": POLICIES,
              "mode": "measurement_only (no privileged state access)", "case_count": len(rows) // len(POLICIES),
              "spec": SPLITS[a.split], "software": {"qiskit": qiskit.__version__, "python": platform.python_version()},
              "summary": summary, "paired_vs_adaptive": paired, "rows": rows,
              "notes": ["Truth labels are evaluator-side; policies never see them.",
                        "'logical_fault' = candidate ideal state violates a declared claim beyond tolerance.",
                        "Rates are descriptive; Wilson intervals assume independent cases, but seeds repeat within a circuit.",
                        "Per-run alpha_total=0.01 union-bounded; case-level false-alarm rate is not tuned."]}
    result["digest"] = digest({k: v for k, v in result.items() if k != "digest"})
    Path(a.out).write_bytes(canonical(result))
    print(json.dumps({"out": a.out, "cases": result["case_count"], "summary": summary, "paired": paired}, indent=1))


if __name__ == "__main__":
    main()
