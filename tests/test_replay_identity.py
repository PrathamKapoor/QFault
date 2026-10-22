from fastapi.testclient import TestClient

from qfault.api import create_app


def test_custom_replay_records_parent_and_distinguishes_new_seed(tmp_path):
    client = TestClient(create_app(tmp_path / 'store'))
    request = {'circuit':{'schema_version':1,'name':'replay input','n_qubits':2,
        'input':{'kind':'computational_basis','bitstring':'00'},'gates':[{'name':'h','qubits':[0]}]},
        'contract':{'kind':'measurement_distribution','basis':'Z','expected_probabilities':{'00':.5,'01':.5},'tolerance':.2}}
    original = client.post('/api/lab/investigations', json=request).json()
    eid = original['experiment_id']
    replay = client.post(f'/api/lab/investigations/{eid}/replay', json={}).json()
    assert replay['experiment_id'] != eid
    assert replay['replay'].get('source_experiment_id') == eid
    assert replay['replay']['semantics'] == 'deterministic_replay'
    rerun = client.post(f'/api/lab/investigations/{eid}/replay', json={'seed':91234}).json()
    assert rerun['configuration']['seed'] == 91234
    assert rerun['replay']['semantics'] == 'new_seed_rerun'
    assert rerun['replay']['source_experiment_id'] == eid
    assert client.get(f'/api/experiments/{eid}').json()['configuration']['seed'] == 42
