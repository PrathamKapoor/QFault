"""The guided inputs must enter the existing engine with traceable provenance."""
import hashlib
import json
from pathlib import Path
import pytest

from fastapi.testclient import TestClient

from qfault.api import create_app
from qfault.counterfactual import RecoveryRequest
from qfault.lab import LabRequest
from qfault.storage import verify_export


def catalog(client):
    response=client.get('/api/guided-demo')
    assert response.status_code==200, 'judges need validated, source-qualified demo inputs'
    return response.json()


def test_guided_catalog_binds_external_reference_candidate_and_independent_contracts(tmp_path):
    client=TestClient(create_app(tmp_path/'store'))
    data=catalog(client)
    source=Path('benchmarks/external/qasmbench/small/qrng_n4/qrng_n4.qasm').read_bytes()
    assert data['source']['sha256']==hashlib.sha256(source).hexdigest()
    assert data['source']['revision']=='357b942396d5c2b7cbc1c229c585a6ef5ccaebac'
    reference=data['reference']['circuit'];candidate=data['candidate']['circuit']
    assert reference['n_qubits']==4
    assert [g['name'] for g in reference['gates']]==['h']*4
    assert candidate['gates'][:-1]==reference['gates']
    assert candidate['gates'][-1]=={'name':'z','qubits':[0],'angle':None}
    assert data['reference']['circuit_id']!=data['candidate']['circuit_id']
    provenance=candidate['import_provenance']
    assert provenance['converted_circuit_id']==data['reference']['circuit_id']
    assert json.loads(provenance['source_representation'])['source_utf8'].encode()==source
    assert all(abs(p-1/16)<1e-12 for p in data['contracts']['z']['expected_probabilities'].values())
    assert any(o['pauli']=='IIIX' and abs(o['expected']-1)<1e-12 for o in data['contracts']['complementary']['observables'])
    for key in ('z','phase','recovery','noise','budget'):
        request=data['requests'][key]
        schema=LabRequest if request['kind']=='investigation' else RecoveryRequest
        parsed=schema.model_validate(request['body'])
        assert parsed.circuit.circuit_id==data['candidate']['circuit_id']
        assert parsed.backend=='aer'
    assert len(data['preview']['candidates'])<=32
    assert any(c['edit']['operator']=='remove' and c['edit']['index']==4 for c in data['preview']['candidates'])
    assert list((tmp_path/'store').glob('experiment_*'))==[], 'catalog generation must not execute measurements'


def test_guided_inputs_execute_real_aer_and_preserve_report_identity(tmp_path):
    client=TestClient(create_app(tmp_path/'store'));data=catalog(client)
    outcomes={};ids=[]
    for key in ('z','phase','recovery','noise','budget'):
        spec=data['requests'][key]
        if spec['kind']=='investigation':
            valid=client.post('/api/lab/validate',json=spec['body'])
            assert valid.status_code==200 and valid.json()['valid']
        response=client.post(spec['endpoint'],json=spec['body'])
        assert response.status_code==201, response.text
        result=response.json();eid=result['experiment_id'];ids.append(eid)
        outcomes[key]=result.get('status',result['diagnosis']['category'])
        report=client.get(f'/api/experiments/{eid}/report').json()
        assert verify_export(report)['valid']
        assert report['investigation']['experiment_id']==eid
        assert report['investigation']['circuit']['import_provenance']==data['candidate']['circuit']['import_provenance']
        if key=='recovery':
            assert result['selection']['candidate_id']==result['selected_candidate']['candidate_id']
            assert result['cost']['phase_shots']['verification_original']>0
            assert result['cost']['phase_shots']['verification_candidate']>0
        if key=='budget':
            assert result['cost']['shots']==0 and result['executions']==[]
    assert len(set(ids))==5
    assert outcomes=={'z':'NO_SIGNIFICANT_DISCREPANCY','phase':'SIGNIFICANT_DISCREPANCY',
        'recovery':'VERIFIED_UNDER_DECLARED_CONTRACT','noise':'NOISE_CONTROL_ABSTENTION','budget':'INSUFFICIENT_BUDGET'}


@pytest.mark.parametrize('payload',[None,[],{'schema_version':True}])
def test_corrupt_guided_inputs_fail_without_execution(tmp_path,monkeypatch,payload):
    import qfault.demo
    (tmp_path/'examples').mkdir()
    (tmp_path/'examples/qrng-phase-demo.json').write_text(json.dumps(payload))
    monkeypatch.setattr(qfault.demo,'ROOT',tmp_path)
    client=TestClient(create_app(tmp_path/'store'))
    response=client.get('/api/guided-demo')
    assert response.status_code==503
    assert list((tmp_path/'store').glob('experiment_*'))==[]
