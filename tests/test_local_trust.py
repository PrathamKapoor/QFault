from fastapi.testclient import TestClient
from qfault.api import create_app


def test_local_server_rejects_untrusted_host_and_cross_origin_write(tmp_path):
    client=TestClient(create_app(tmp_path/'store'))
    assert client.get('/api/health',headers={'host':'attacker.example'}).status_code==400
    response=client.post('/api/lab/investigations',json={},headers={'origin':'https://attacker.example'})
    assert response.status_code==403
    assert client.get('/api/health').status_code==200
    assert client.post('/api/lab/investigations',json={},headers={'origin':'http://testserver'}).status_code==422
