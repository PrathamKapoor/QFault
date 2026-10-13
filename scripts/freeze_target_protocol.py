"""Write configs/target-witness-protocol.json: frozen corpus, budgets, policies, metrics and source digests."""
import hashlib
import json
import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from qfault.target_corpus import BUDGETS, ENVIRONMENTS, SPLITS, TOLERANCE, cases
from qfault.target import CATALOG_VERSION, POLICY_VERSION
from scripts.evaluate_target import POLICIES

sources = ["qfault/target.py", "qfault/lab.py", "qfault/target_corpus.py", "scripts/evaluate_target.py"]
protocol = {
    "protocol": "target-witness-v1", "frozen_before_holdout_execution": True,
    "splits": SPLITS, "budgets": BUDGETS, "environments": ENVIRONMENTS, "fidelity_tolerance": TOLERANCE,
    "policies": POLICIES, "policy_version": POLICY_VERSION, "catalog_version": CATALOG_VERSION,
    "diagnostic_mode": "measurement_only", "backends": ["reference (primary)", "aer (replication)"],
    "case_counts": {s: len(cases(s)) for s in SPLITS},
    "metrics": {
        "detection": "SIGNIFICANT_DISCREPANCY among logical_violation cases (ideal fidelity < 1 - tolerance)",
        "false_alarm": "SIGNIFICANT_DISCREPANCY among clean_correct cases (ideal environment, ideal fidelity >= threshold)",
        "confirmation": "NO_SIGNIFICANT_DISCREPANCY among clean_correct cases",
        "coverage": "effective fidelity inside [L,U]; defined only without gate noise",
        "width": "U - L of the final measured fidelity bound",
        "cost": "shots, circuit evaluations, basis gates, local runtime",
        "paired": "per-case baseline minus adaptive_witness, bootstrap 95% (2000 resamples, seed 20261013)"},
    "stopping": "decision reached / look limit / shot or evaluation budget / no informative action (adaptive only)",
    "exclusions": "none; failed or aborted runs are reported",
    "development_note": "Development split was run once (196 cases); no policy change followed it.",
    "source_sha256": {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in sources}}
(root / "configs" / "target-witness-protocol.json").write_text(json.dumps(protocol, indent=1, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(protocol["case_counts"]), protocol["source_sha256"])
