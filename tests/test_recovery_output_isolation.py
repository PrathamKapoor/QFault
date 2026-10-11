"""A genuine recovery reproduction must never publish over existing benchmark evidence."""
import json,runpy,sys

def test_recovery_reproduction_preserves_existing_benchmark(tmp_path,monkeypatch):
    benchmark=tmp_path/'benchmarks'/'recovery-stabilization.json'
    benchmark.parent.mkdir()
    original=b'{"preserved_release_evidence":true}\n'
    benchmark.write_bytes(original)
    output=tmp_path/'recovery'
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys,'argv',['evaluate_recovery','--out',str(output)])
    runpy.run_module('scripts.evaluate_recovery',run_name='__main__')
    assert benchmark.read_bytes()==original
    summary=json.loads((output/'summary.json').read_bytes())
    assert summary['verified']['n']==12
    assert {c['status'] for c in summary['controls']}=={'REJECTED'}
