from qfault.cli import main


def test_report_verification_rejects_oversize_before_parsing(tmp_path,capsys,monkeypatch):
    path=tmp_path/'huge.json';path.write_bytes(b' '*((16*1024*1024)+1))
    def forbidden(*args):raise AssertionError('oversized input reached verifier')
    monkeypatch.setattr('qfault.storage.verify_export',forbidden)
    assert main(['verify-report',str(path)])==1
    assert '16 MiB' in capsys.readouterr().err
