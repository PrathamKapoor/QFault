"""Rebuild the pinned, bounded QASMBench inventory without network access.

The source tree accounts for every upstream .qasm blob. Only canonical originals
whose filename declares 2..5 qubits are vendored and inspected. Transpiled variants
are duplicates, never additional independent architectures. No diagnostic outcome
is read when eligibility and the deterministic development/holdout split are built.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from qfault.qasm_import import (BASIS, MAX_SOURCE_BYTES, MAX_SOURCE_INSTRUCTIONS,
                               MAX_TRANSFORMED_GATES, STANDARD_GATES,
                               QASMImportError, import_qasm2)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "benchmarks/external/qasmbench"
REPOSITORY = "https://github.com/pnnl/QASMBench"
COMMIT = "357b942396d5c2b7cbc1c229c585a6ef5ccaebac"


def _git_blob_sha(raw):
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def build_inventory(*, tree_path=None, source_root=None):
    """Inventory all pinned paths and return JSON-ready reproducible metadata."""
    source_root = Path(source_root) if source_root else SOURCE_ROOT
    tree_path = Path(tree_path) if tree_path else source_root / "upstream-tree.json"
    tree = json.loads(tree_path.read_text(encoding="utf-8"))
    if tree["sha"] != COMMIT or tree.get("truncated"):
        raise ValueError("upstream tree must be complete and at the pinned commit")
    blobs = {entry["path"]: entry for entry in tree["tree"] if entry["type"] == "blob"}
    licensing = {}
    for filename in ("LICENSE", "NOTICE"):
        raw = (source_root / filename).read_bytes()
        if _git_blob_sha(raw) != blobs[filename]["sha"]:
            raise ValueError(f"vendored {filename} does not match pinned Git blob")
        licensing[filename.lower() + "_sha256"] = hashlib.sha256(raw).hexdigest()
        licensing[filename.lower() + "_blob_sha"] = blobs[filename]["sha"]
    entries = []
    for path, blob in sorted(blobs.items()):
        if not path.endswith(".qasm"):
            continue
        inferred = re.findall(r"(?:_n|_N)(\d+)", path)
        declared = int(inferred[-1]) if inferred else None
        duplicate = Path(path).stem.endswith("_transpiled")
        entry = {"source_repository": REPOSITORY, "source_repo_sha": COMMIT,
                 "source_path": path, "source_url": f"{REPOSITORY}/blob/{COMMIT}/{path}",
                 "blob_sha": blob["sha"], "source_bytes": blob["size"], "sha256": None,
                 "license": "LicenseRef-QASMBench-Battelle", **licensing,
                 "variant": "transpiled_duplicate" if duplicate else "canonical_original",
                 "canonical_source_path": path.replace("_transpiled.qasm", ".qasm") if duplicate else path,
                 "filename_n_qubits": declared, "qubit_count_basis": "upstream filename, unparsed",
                 "raw_n_qubits": None, "raw_depth": None, "raw_gate_counts": None,
                 "raw_vocabulary": None, "has_measurements": None,
                 "has_classical_control": None, "inspection_level": "upstream_tree_only",
                 "canonical_input": None, "transformations": None,
                 "measurement_mapping": None, "transformed_gate_count": None,
                 "transformed_depth": None, "operator_equivalent": None,
                 "basis_inputs_checked": None, "circuit": None, "provenance": None,
                 "status": "excluded", "split": None, "reason_code": None, "reason": None}
        if duplicate:
            entry.update(reason_code="transpiled_duplicate",
                         reason="upstream transpiled variant of a canonical source; not an independent architecture")
        elif declared is None:
            entry.update(reason_code="unknown_filename_qubit_count",
                         reason="cannot establish bounded qubit count from upstream path before parsing")
        elif not 2 <= declared <= 5:
            entry.update(reason_code="qubit_limit",
                         reason=f"filename declares {declared} qubits, outside 2..5; source not downloaded or parsed")
        elif blob["size"] > MAX_SOURCE_BYTES:
            entry.update(reason_code="source_size_limit",
                         reason=f"Git blob size exceeds {MAX_SOURCE_BYTES} bytes; source not parsed")
        else:
            raw = (source_root / path).read_bytes()
            if _git_blob_sha(raw) != blob["sha"]:
                raise ValueError(f"vendored source does not match pinned Git blob: {path}")
            try:
                imported = import_qasm2(raw, name=Path(path).stem)
                provenance = imported["provenance"]
                entry.update({k: provenance[k] for k in entry if k in provenance})
                entry.update(status="eligible", circuit=imported["circuit"], provenance=provenance,
                             reason_code=None, reason=None, qubit_count_basis="parsed qreg declarations")
                if provenance["raw_n_qubits"] != declared:
                    raise ValueError(f"source qubit declarations disagree with filename: {path}")
            except QASMImportError as error:
                entry.update({k: value for k, value in error.metadata.items() if k in entry})
                entry.update(reason_code=error.code, reason=str(error))
                if entry["raw_n_qubits"] is not None:
                    entry["qubit_count_basis"] = "bounded lexical or parsed qreg declarations"
        entries.append(entry)
    eligible = [e for e in entries if e["status"] == "eligible"]
    for index, entry in enumerate(eligible):
        entry["split"] = "development" if index % 3 == 0 else "holdout"
    return {"schema_version": 1, "corpus_id": "qasmbench-static-2to5-v1",
            "source_repository": REPOSITORY, "source_repo_sha": COMMIT,
            "tree_sha256": hashlib.sha256(tree_path.read_bytes()).hexdigest(),
            "scope": "all upstream .qasm paths inventoried; canonical 2..5-qubit originals inspected",
            "limits": {"min_qubits": 2, "max_qubits": 5, "max_source_bytes": MAX_SOURCE_BYTES,
                       "max_source_instructions": MAX_SOURCE_INSTRUCTIONS,
                       "max_transformed_gates": MAX_TRANSFORMED_GATES},
            "allowed_standard_gates": sorted(STANDARD_GATES), "output_basis": list(BASIS),
            "input_policy": "canonical all-zero computational-basis input",
            "split_policy": {"stage": "before any diagnostic outcomes", "ordering": "source_path ascending",
                             "development": "eligible index modulo 3 equals 0", "holdout": "remaining eligible paths",
                             "outcome_independent": True},
            "summary": {"total_qasm_paths": len(entries),
                        "variants": dict(sorted(Counter(e["variant"] for e in entries).items())),
                        "statuses": dict(sorted(Counter(e["status"] for e in entries).items())),
                        "exclusion_reasons": dict(sorted(Counter(e["reason_code"] for e in entries if e["status"] == "excluded").items())),
                        "splits": dict(sorted(Counter(e["split"] for e in eligible).items()))},
            "entries": entries}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "configs/external-corpus.json")
    args = parser.parse_args()
    inventory = build_inventory()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(inventory["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
