from qfault.evidence import canonical, digest
from qfault.storage import ArtifactStore, verify_export
from qfault.workflow import RunRequest, investigate


def test_unknown_manifest_version_fails_even_when_hashes_match(tmp_path):
    store=ArtifactStore(tmp_path)
    eid=store.save(investigate(RunRequest(shots=128,max_shots=256,max_evaluations=2,recover=False)))
    report=store.export(eid)
    report['manifest']['schema_version']=999
    assert not verify_export(report)['valid']
    (store.folder(eid)/'manifest.json').write_bytes(canonical(report['manifest']))
    assert not store.verify(eid)['valid']


def test_unknown_investigation_version_fails_despite_rehash(tmp_path):
    store=ArtifactStore(tmp_path)
    eid=store.save(investigate(RunRequest(shots=128,max_shots=256,max_evaluations=2,recover=False)))
    report=store.export(eid)
    report['investigation']['schema_version']=999
    report['manifest']['artifacts']['investigation.json']=digest(report['investigation'])
    assert not verify_export(report)['valid']


def test_unknown_blind_export_version_is_not_silently_reinterpreted(tmp_path):
    from fastapi.testclient import TestClient
    from qfault.api import create_app
    client=TestClient(create_app(tmp_path/'store'))
    cid=client.post('/api/challenges',json={'seed':91737}).json()['challenge_id']
    report=client.get(f'/api/challenges/{cid}/report').json()
    assert verify_export(report)['valid']
    report['schema_version']=999
    assert not verify_export(report)['valid']
