"""Exercise every participant route, not merely DOM concealment."""
import copy
import json
import pytest
from fastapi.testclient import TestClient
from qfault.api import create_app
from qfault.storage import verify_export
from qfault.evidence import digest


PRIVATE_KEYS={'evaluation_truth','noise_configuration','input_digest','scenario','mutation',
              'original_gate','selection_seed','seed','candidate','circuit_id','subject_circuit_id'}


def assert_private_absent(value):
    if isinstance(value,dict):
        assert not PRIVATE_KEYS.intersection(value),PRIVATE_KEYS.intersection(value)
        for v in value.values():assert_private_absent(v)
    elif isinstance(value,list):
        for v in value:assert_private_absent(v)


def start(client,**options):
    response=client.post('/api/challenges',json={'seed':91737,**options})
    assert response.status_code==201,response.text
    return response.json()


@pytest.mark.parametrize('mode',['measurement_only','simulator_assisted'])
def test_all_pre_reveal_routes_and_order(tmp_path,mode):
    client=TestClient(create_app(tmp_path))
    r=start(client,diagnostic_mode=mode,recover=mode=='simulator_assisted')
    cid=r['challenge_id'];url='/api/challenges/'+cid
    assert r['state']=='OBSERVED' and r['diagnosis'] is None
    assert client.post(url+'/reveal').status_code==409
    assert client.post(url+'/freeze').status_code==409
    assert client.post(url+'/replay').status_code==409
    assert client.post(url+'/diagnose').status_code==200
    diagnosed=client.get(url).json()
    assert sum(r['executed_shots'] for r in diagnosed['measurements']+diagnosed['diagnostic_measurements'])==diagnosed['cost']['shots']
    for path in [url,'/api/challenges',url+'/report',url+'/verification','/api/experiments']:
        payload=client.get(path).json();assert_private_absent(payload)
    report=client.get(url+'/report').json()
    assert verify_export(report)['valid']
    assert report['state']=='DIAGNOSED'
    frozen=client.post(url+'/freeze').json()
    assert frozen['state']=='FROZEN'
    assert_private_absent(frozen)
    assert client.post(url+'/diagnose').status_code==409
    fresh=TestClient(create_app(tmp_path))
    assert fresh.get(url).json()['state']=='FROZEN'
    revealed=fresh.post(url+'/reveal').json()
    assert revealed['state']=='REVEALED'
    assert revealed['freeze']['prediction_digest']==revealed['reveal']['prediction_digest']
    assert revealed['reveal']['sequence']>revealed['freeze']['sequence']
    exported=fresh.get(url+'/report').json()
    assert verify_export(exported)['valid']
    altered=copy.deepcopy(exported)
    nested=altered['revealed_investigation']
    nested['investigation']['diagnosis']['reason']='Different private prediction'
    nested['investigation']['prediction_digest']=digest({'diagnosis':nested['investigation']['diagnosis'],'recovery':nested['investigation']['recovery']})
    nested['manifest']['artifacts']['investigation.json']=digest(nested['investigation'])
    assert verify_export(nested)['valid']
    assert not verify_export(altered)['valid']  # must bind the private prediction to the public freeze
    assert exported['revealed_investigation']['evaluation']['scenario']
    eid=exported['revealed_investigation']['investigation']['experiment_id']
    for suffix in ['', '/report','/verification']:
        assert fresh.get('/api/experiments/'+eid+suffix).status_code==404
    tampered=copy.deepcopy(exported)
    tampered['documents']['diagnosed']['diagnosis']['category']='FORGED'
    assert not verify_export(tampered)['valid']
    replay=fresh.post(url+'/replay');assert replay.status_code==201
    assert replay.json()['measurements']==r['measurements'] or [x['output_counts'] for x in replay.json()['measurements']]==[x['output_counts'] for x in r['measurements']]
    assert fresh.get(url).json()['state']=='REVEALED'


def test_bad_budgets_and_invalid_pool(tmp_path):
    client=TestClient(create_app(tmp_path))
    for body in [{'shots':0},{'shots':2048,'max_shots':100},{'pool':'guaranteed_success'},
                 {'family':'bell','n_qubits':3},{'diagnostic_mode':'measurement_only','recover':True}]:
        assert client.post('/api/challenges',json=body).status_code==422
    assert client.get('/api/challenges/not-an-id').status_code==422


def test_low_budget_abstention_and_corrupt_freeze(tmp_path):
    client=TestClient(create_app(tmp_path))
    r=start(client,shots=64,max_shots=128)
    url='/api/challenges/'+r['challenge_id']
    diagnosed=client.post(url+'/diagnose').json()
    assert diagnosed['diagnosis']['category']=='INSUFFICIENT_EVIDENCE'
    client.post(url+'/freeze')
    file=tmp_path/'challenges'/r['challenge_id']/'freeze.json'
    value=json.loads(file.read_bytes());value['prediction_digest']='0'*64;file.write_text(json.dumps(value))
    assert client.post(url+'/reveal').status_code==422


def test_ordinary_investigation_still_available(tmp_path):
    client=TestClient(create_app(tmp_path))
    response=client.post('/api/experiments',json={'scenario':'clean','recover':False})
    assert response.status_code==201
    assert response.json()['diagnosis']['category']=='NO_SIGNIFICANT_FAILURE_DETECTED'


def test_clean_control_and_evaluator_is_only_called_after_freeze(tmp_path,monkeypatch):
    from qfault import experiments
    original=experiments.evaluator_truth
    def forbidden(*args):raise AssertionError('Evaluator consulted before reveal')
    monkeypatch.setattr(experiments,'evaluator_truth',forbidden)
    client=TestClient(create_app(tmp_path))
    r=start(client,seed=2)
    url='/api/challenges/'+r['challenge_id']
    diagnosed=client.post(url+'/diagnose').json()
    assert diagnosed['diagnosis']['category']=='NO_SIGNIFICANT_FAILURE_DETECTED'
    assert client.post(url+'/freeze').json()['state']=='FROZEN'
    assert client.post(url+'/freeze').json()['state']=='FROZEN'
    monkeypatch.setattr(experiments,'evaluator_truth',original)
    revealed=client.post(url+'/reveal').json()
    assert revealed['reveal']['evaluation_truth']['scenario']=='clean'
    assert client.post(url+'/reveal').json()==revealed


def test_history_and_saved_view_reads_can_arrive_together(tmp_path,monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    from qfault.challenge import BlindChallenges
    entered=Event();release=Event();original=BlindChallenges.list
    def paused(self):
        entered.set();assert release.wait(3)
        return original(self)
    monkeypatch.setattr(BlindChallenges,'list',paused)
    client=TestClient(create_app(tmp_path));r=start(client)
    with ThreadPoolExecutor(2) as pool:
        history=pool.submit(client.get,'/api/challenges')
        assert entered.wait(3)
        saved=pool.submit(client.get,'/api/challenges/'+r['challenge_id'])
        release.set()
        assert history.result().status_code==200
        assert saved.result().status_code==200


def test_execution_error_does_not_disclose_private_configuration(tmp_path,monkeypatch):
    import qfault.challenge as challenge
    def failed(*args):raise RuntimeError('private scenario=phase seed=999')
    monkeypatch.setattr(challenge,'observe',failed)
    response=TestClient(create_app(tmp_path)).post('/api/challenges',json={})
    assert response.status_code==422
    assert 'scenario=phase' not in response.text and 'seed=999' not in response.text


def test_blind_recovery_projection_and_independent_verification(tmp_path):
    client=TestClient(create_app(tmp_path))
    r=start(client,seed=1,diagnostic_mode='simulator_assisted',recover=True)
    url='/api/challenges/'+r['challenge_id']
    diagnosed=client.post(url+'/diagnose').json()
    assert_private_absent(diagnosed)
    assert diagnosed['recovery']['verification']['verified_status']=='VERIFIED'
    assert 'privileged simulator' in diagnosed['recovery']['capability_mode']
    client.post(url+'/freeze')
    revealed=client.post(url+'/reveal').json()
    assert revealed['reveal']['evaluation_truth']['scenario']=='remove'
    assert revealed['reveal']['comparison']['category_match']
