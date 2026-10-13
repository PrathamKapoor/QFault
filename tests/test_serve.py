"""Local server launcher: localhost only, explicit port, clear failure when the port is taken."""
import socket
import pytest
from qfault import api, cli


def test_occupied_port_fails_fast_with_message(capsys):
    held = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    held.bind(("127.0.0.1", 0)); held.listen(1)
    port = held.getsockname()[1]
    try:
        with pytest.raises(SystemExit) as stop:
            api.main(port)
        assert stop.value.code == 2
        assert f"127.0.0.1:{port} is already in use" in capsys.readouterr().err
    finally:
        held.close()


def test_cli_passes_port_and_keeps_localhost(monkeypatch):
    import inspect
    assert 'host="127.0.0.1"' in inspect.getsource(api.main)  # never binds all interfaces
    seen = {}
    monkeypatch.setattr(api, "main", lambda port=8000: seen.setdefault("port", port))
    assert cli.main(["serve", "--port", "8123"]) == 0
    assert seen["port"] == 8123
