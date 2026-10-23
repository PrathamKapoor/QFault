import json
import numpy as np
from fastapi.testclient import TestClient
from qfault.api import create_app

def test_external_entangling_catalog_is_imported_and_reference_is_not_candidate(tmp_path):
 app=TestClient(create_app(tmp_path));response=app.get('/api/guided-demo?example=cat')
 assert response.status_code==200
 data=response.json();assert data['id']=='qasmbench-cat-phase-v1'
 assert data['source']['path']=='small/cat_state_n4/cat_state_n4.qasm'
 assert any(g['name']=='cx' for g in data['reference']['circuit']['gates'])
 assert data['reference']['circuit_id']!=data['candidate']['circuit_id']
 from qiskit import QuantumCircuit
 from qiskit.quantum_info import Statevector,partial_trace
 source=json.loads(data['reference']['circuit']['import_provenance']['source_representation'])['source_utf8']
 circuit=QuantumCircuit.from_qasm_str(source);circuit.remove_final_measurements()
 state=Statevector.from_instruction(circuit)
 assert np.allclose(state.probabilities(),[.5]+[0]*14+[.5])
 assert np.isclose(np.trace(partial_trace(state,[1,2,3]).data@partial_trace(state,[1,2,3]).data),.5)

def test_entangling_demo_executes_existing_engine_and_preserves_exports(tmp_path):
 from qfault.storage import verify_export
 app=TestClient(create_app(tmp_path));data=app.get('/api/guided-demo?example=cat').json()
 assert data['id']=='qasmbench-cat-phase-v1'
 results=[]
 for key in ('z','phase','recovery'):
  spec=data['requests'][key];r=app.post(spec['endpoint'],json=spec['body']);assert r.status_code==201,r.text
  result=r.json();results.append(result)
  assert verify_export(app.get('/api/experiments/'+result['experiment_id']+'/report').json())['valid']
 assert results[0]['diagnosis']['category']=='NO_SIGNIFICANT_DISCREPANCY'
 assert results[1]['diagnosis']['category']=='SIGNIFICANT_DISCREPANCY'
 assert results[2]['status']=='VERIFIED_UNDER_DECLARED_CONTRACT'
 assert results[2]['circuit_id']==data['candidate']['circuit_id']
