import json
import pytest
from fastapi.testclient import TestClient
from qfault.api import create_app
from qfault.storage import ArtifactStore
from qfault.workflow import investigate,RunRequest

@pytest.mark.parametrize('bad',[None,[],{}])
@pytest.mark.parametrize('artifact',['investigation','review'])
def test_corrupt_artifact_returns_integrity_failure(tmp_path,bad,artifact):
    store=ArtifactStore(tmp_path)
    eid=store.save(investigate(RunRequest(shots=128,recover=False)))
    if artifact=='review':
        store.review(eid,'reviewer','acknowledge','Reviewed')
        path=next((tmp_path/eid).glob('review_*.json'))
    else:
        path=tmp_path/eid/'investigation.json'
    path.write_text(json.dumps(bad),encoding='utf8')
    client=TestClient(create_app(tmp_path))
    response=client.get(f'/api/experiments/{eid}/verification')
    assert response.status_code==200
    assert response.json()['valid'] is False
    assert client.get(f'/api/experiments/{eid}').status_code==422
    assert client.get('/api/experiments').json()[0]['integrity_valid'] is False

def test_deleted_review_is_detected(tmp_path):
    store=ArtifactStore(tmp_path)
    eid=store.save(investigate(RunRequest(shots=128,recover=False)))
    store.review(eid,'reviewer','acknowledge','Reviewed')
    assert store.verify(eid)['valid']
    next((tmp_path/eid).glob('review_*.json')).unlink()
    assert not store.verify(eid)['valid']
