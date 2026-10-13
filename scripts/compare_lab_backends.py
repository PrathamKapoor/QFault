"""Case-by-case comparison of two custom-lab evaluation files (e.g. reference vs Aer).

Usage: python scripts/compare_lab_backends.py A.json B.json --out benchmarks/<name>.json
Sampled counts legitimately differ between simulators; this reports agreement, not identity.
"""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qfault.evidence import canonical, digest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a"); ap.add_argument("b"); ap.add_argument("--out", required=True)
    args = ap.parse_args()
    A, B = (json.loads(Path(p).read_bytes()) for p in (args.a, args.b))
    key = lambda r: (r["case_id"], r["policy"])
    ra, rb = {key(r): r for r in A["rows"]}, {key(r): r for r in B["rows"]}
    if set(ra) != set(rb):
        raise SystemExit("row sets differ; files are not the same prespecified cases")
    disagreements, by_policy = [], {}
    for k in sorted(ra):
        x, y = ra[k], rb[k]
        p = by_policy.setdefault(k[1], {"rows": 0, "category_agree": 0, "shots_equal": 0, "shot_diff_sum": 0,
                                         "runtime_a": 0.0, "runtime_b": 0.0})
        p["rows"] += 1
        p["category_agree"] += x["category"] == y["category"]
        p["shots_equal"] += x["shots"] == y["shots"]
        p["shot_diff_sum"] += y["shots"] - x["shots"]
        p["runtime_a"] += x["runtime_seconds"]; p["runtime_b"] += y["runtime_seconds"]
        if x["category"] != y["category"] or x["attribution"] != y["attribution"]:
            disagreements.append({"case_id": k[0], "policy": k[1], "truth_class": x["truth_class"],
                                  "a": [x["category"], x["attribution"], x["shots"]],
                                  "b": [y["category"], y["attribution"], y["shots"]]})
    by_class = {}
    for d in disagreements:
        by_class[d["truth_class"]] = by_class.get(d["truth_class"], 0) + 1
    result = {"a": {"file": args.a, "backend": A["backend"], "digest": A["digest"]},
              "b": {"file": args.b, "backend": B["backend"], "digest": B["digest"]},
              "rows": len(ra), "by_policy": by_policy, "disagreements_by_truth_class": by_class,
              "disagreements": disagreements,
              "summary_a": A["summary"], "summary_b": B["summary"],
              "notes": ["Different simulators draw different samples for the same seed; near-threshold decisions may flip.",
                        "Systematic disagreement would appear as one-directional category shifts within a truth class."]}
    result["digest"] = digest({k: v for k, v in result.items() if k != "digest"})
    Path(args.out).write_bytes(canonical(result))
    print(json.dumps({k: result[k] for k in ("rows", "by_policy", "disagreements_by_truth_class")}, indent=1))
    for d in disagreements: print(d)


if __name__ == "__main__":
    main()
