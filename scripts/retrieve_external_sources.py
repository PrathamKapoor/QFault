"""Verify or retrieve the frozen bounded QASMBench sources using only stdlib.

Default verification is offline. --out downloads the pinned canonical 2..5-qubit
sources and licensing into a new directory; existing output is never overwritten.
No QASM is parsed or executed, and no QASM include is opened.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import quote
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "benchmarks/external/qasmbench"
MANIFEST = ROOT / "configs/external-corpus.json"
COMMIT = "357b942396d5c2b7cbc1c229c585a6ef5ccaebac"
RAW_PREFIX = f"https://raw.githubusercontent.com/pnnl/QASMBench/{COMMIT}/"
MAX_SOURCE_BYTES = 65536
MAX_TREE_BYTES = 4 * 1024 * 1024


def _path(root, relative):
    if (not isinstance(relative, str) or not relative or "\\" in relative or ":" in relative
            or relative.startswith("/") or any(p in ("", ".", "..") for p in relative.split("/"))):
        raise ValueError("unsafe source path: " + repr(relative))
    pure = PurePosixPath(relative)
    root = Path(root).resolve()
    result = root.joinpath(*pure.parts)
    if not result.resolve().is_relative_to(root):
        raise ValueError("source path escapes root: " + relative)
    return result


def _read_bounded(path, maximum):
    with Path(path).open("rb") as stream:
        raw = stream.read(maximum + 1)
    if len(raw) > maximum:
        raise ValueError("source size exceeds bounded read: " + str(path))
    return raw


def _check(raw, spec):
    if len(raw) != spec["size"] or len(raw) > MAX_SOURCE_BYTES:
        raise ValueError("source size mismatch: " + spec["path"])
    blob_sha = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
    if blob_sha != spec["blob_sha"]:
        raise ValueError("Git blob checksum mismatch: " + spec["path"])
    if hashlib.sha256(raw).hexdigest() != spec["sha256"]:
        raise ValueError("SHA256 checksum mismatch: " + spec["path"])


def _specs(manifest_path, source_root):
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    if manifest["source_repo_sha"] != COMMIT:
        raise ValueError("unexpected repository commit")
    tree_raw = _read_bounded(_path(source_root, "upstream-tree.json"), MAX_TREE_BYTES)
    if hashlib.sha256(tree_raw).hexdigest() != manifest["tree_sha256"]:
        raise ValueError("upstream tree SHA256 checksum mismatch")
    tree = json.loads(tree_raw)
    if tree["sha"] != COMMIT or tree.get("truncated"):
        raise ValueError("upstream tree must be complete and pinned")
    blobs = {e["path"]: e for e in tree["tree"] if e["type"] == "blob"}
    bounded = set()
    for path in blobs:
        if path.endswith(".qasm") and not path.endswith("_transpiled.qasm"):
            counts = re.findall(r"(?:_n|_N)(\d+)", path)
            if counts and 2 <= int(counts[-1]) <= 5:
                bounded.add(path)
    indexed = {}
    for entry in manifest["entries"]:
        path = entry["source_path"]
        _path(source_root, path)
        if path in indexed:
            raise ValueError("duplicate source path in inventory: " + path)
        indexed[path] = entry
    if not bounded <= indexed.keys():
        raise ValueError("frozen inventory omits bounded source paths")
    specs = []
    for path in sorted(bounded):
        entry, blob = indexed[path], blobs[path]
        if entry["variant"] != "canonical_original" or entry["blob_sha"] != blob["sha"] or entry["source_bytes"] != blob["size"]:
            raise ValueError("frozen source metadata disagrees with Git tree: " + path)
        if not isinstance(entry["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]):
            raise ValueError("missing frozen source SHA256: " + path)
        specs.append({"path": path, "size": blob["size"], "blob_sha": blob["sha"], "sha256": entry["sha256"]})
    for path in ("LICENSE", "NOTICE"):
        field = path.lower()
        sha256s = {e[field + "_sha256"] for e in indexed.values()}
        blob_shas = {e[field + "_blob_sha"] for e in indexed.values()}
        if len(sha256s) != 1 or blob_shas != {blobs[path]["sha"]}:
            raise ValueError("inconsistent frozen licensing checksum")
        specs.append({"path": path, "size": blobs[path]["size"], "blob_sha": blobs[path]["sha"], "sha256": sha256s.pop()})
    if any(not isinstance(s["size"], int) or not 0 <= s["size"] <= MAX_SOURCE_BYTES for s in specs):
        raise ValueError("source size outside bounded retrieval limit")
    return specs, tree_raw, len(bounded)


def verify_sources(*, source_root=None, manifest_path=None):
    """Check every vendored bounded source, LICENSE, NOTICE and frozen tree."""
    source_root = Path(source_root) if source_root is not None else SOURCE_ROOT
    specs, _, count = _specs(manifest_path or MANIFEST, source_root)
    for spec in specs:
        _check(_read_bounded(_path(source_root, spec["path"]), MAX_SOURCE_BYTES), spec)
    return {"repository_commit": COMMIT, "canonical_sources": count,
            "files_verified": len(specs) + 1, "sha256_and_git_blob_verified": True}


def _write_new(root, relative, raw):
    path = _path(root, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(raw)


def download_sources(out, *, manifest_path=None):
    """Fetch only frozen raw GitHub paths, bounded before writing each file.

    A failed retrieval leaves an incomplete new directory for inspection. A fresh
    output path is required to retry; no pre-existing file is overwritten.
    """
    manifest_path = manifest_path or MANIFEST
    specs, tree_raw, _ = _specs(manifest_path, SOURCE_ROOT)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    _write_new(out, "upstream-tree.json", tree_raw)
    for spec in specs:
        url = RAW_PREFIX + quote(spec["path"], safe="/")
        with urlopen(url, timeout=30) as response:
            raw = response.read(MAX_SOURCE_BYTES + 1)
        _check(raw, spec)
        _write_new(out, spec["path"], raw)
    return verify_sources(source_root=out, manifest_path=manifest_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="offline verification (default)")
    parser.add_argument("--root", type=Path, default=SOURCE_ROOT, help="source bundle to verify")
    parser.add_argument("--out", type=Path, help="new directory for pinned download")
    args = parser.parse_args()
    if args.out and args.verify:
        parser.error("choose either --verify or --out")
    report = download_sources(args.out) if args.out else verify_sources(source_root=args.root)
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
