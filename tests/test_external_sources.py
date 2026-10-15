"""Pinned source checks fail closed before source interpretation or overwrites."""
import io
import json
from pathlib import Path
import shutil

import pytest


def retrieval():
    import scripts
    assert (Path(scripts.__file__).parent / "retrieve_external_sources.py").exists(), "retrieval verification missing"
    from scripts import retrieve_external_sources
    return retrieve_external_sources


def test_verify_covers_all_bounded_sources_and_licensing_without_network(monkeypatch):
    tool = retrieval()
    monkeypatch.setattr(tool, "urlopen", lambda *args, **kwargs: pytest.fail("verification used network"))
    report = tool.verify_sources()
    assert report["canonical_sources"] == 31
    assert report["files_verified"] == 34  # all sources, license, notice, upstream tree
    assert report["repository_commit"] == "357b942396d5c2b7cbc1c229c585a6ef5ccaebac"


def test_verify_rejects_source_tampering_before_acceptance(tmp_path):
    tool = retrieval()
    shutil.copytree(tool.SOURCE_ROOT, tmp_path / "copy")
    sample = tmp_path / "copy/small/deutsch_n2/deutsch_n2.qasm"
    original = sample.read_bytes()
    assert b"h q[0]" in original
    sample.write_bytes(original.replace(b"h q[0]", b"x q[0]", 1))
    with pytest.raises(ValueError, match="checksum|blob|size"):
        tool.verify_sources(source_root=tmp_path / "copy")


def test_verify_checks_frozen_sha256_even_when_git_blob_is_correct(tmp_path):
    tool = retrieval()
    manifest = json.loads(tool.MANIFEST.read_text(encoding="utf-8"))
    candidate = next(e for e in manifest["entries"] if e["sha256"] is not None)
    candidate["sha256"] = "0" * 64
    modified = tmp_path / "manifest.json"
    modified.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="SHA256"):
        tool.verify_sources(manifest_path=modified)


@pytest.mark.parametrize("path", ["../escape.qasm", "/absolute.qasm", "C:/escape.qasm", "a\\escape.qasm", "a/../escape.qasm", "https://evil/source.qasm"])
def test_untrusted_inventory_paths_cannot_escape_root(path, tmp_path):
    tool = retrieval()
    manifest = json.loads(tool.MANIFEST.read_text(encoding="utf-8"))
    candidate = next(e for e in manifest["entries"] if e["sha256"] is not None)
    candidate["source_path"] = path
    malformed = tmp_path / "manifest.json"
    malformed.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="path"):
        tool.verify_sources(manifest_path=malformed)


def test_download_uses_pinned_urls_and_refuses_existing_output(tmp_path, monkeypatch):
    tool = retrieval()
    seen = []
    prefix = "https://raw.githubusercontent.com/pnnl/QASMBench/357b942396d5c2b7cbc1c229c585a6ef5ccaebac/"
    def fetch(url, timeout):
        assert url.startswith(prefix)
        seen.append(url)
        return io.BytesIO((tool.SOURCE_ROOT / url[len(prefix):]).read_bytes())
    monkeypatch.setattr(tool, "urlopen", fetch)
    out = tmp_path / "new-download"
    report = tool.download_sources(out)
    assert report["canonical_sources"] == 31
    assert len(seen) == 33
    with pytest.raises(FileExistsError):
        tool.download_sources(out)


def test_oversized_download_stops_at_bounded_read_and_never_writes_source(tmp_path, monkeypatch):
    tool = retrieval()
    class Oversized(io.BytesIO):
        def read(self, size=-1):
            assert 0 < size <= 65537
            return super().read(size)
    monkeypatch.setattr(tool, "urlopen", lambda *args, **kwargs: Oversized(b"x" * 70000))
    out = tmp_path / "oversized"
    with pytest.raises(ValueError, match="size"):
        tool.download_sources(out)
    assert not list(out.rglob("*.qasm"))
