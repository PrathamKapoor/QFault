import time
import pytest
from tests.test_hosting import MemoryState

def test_global_admission_between_independent_instances_and_release():
 from qfault.hosted_admission import Admission,Busy
 storage=MemoryState();a=Admission(storage);b=Admission(storage)
 lease=a.acquire(200000)
 with pytest.raises(Busy):b.acquire(1000)
 a.release(lease);other=b.acquire(1000);b.release(other)
 state=storage.read('global-admission-v1')[0]
 assert state['reserved_shots']==201000 and state['admitted']==2

def test_expired_lease_and_daily_reservation_cap_are_distinct():
 from qfault.hosted_admission import Admission,Busy
 storage=MemoryState();a=Admission(storage);lease=a.acquire(100)
 row=storage.rows['global-admission-v1'][0];row['slots'][lease]=1
 assert a.acquire(100)
 row=storage.rows['global-admission-v1'][0];row['slots']={};row['reserved_shots']=5000000
 with pytest.raises(Busy):a.acquire(1)

def test_compressed_snapshot_roundtrip_preserves_raw_bytes_and_legacy():
 from qfault.hosted_codec import encode_state,decode_state
 from qfault.hosting import empty_state
 import json
 state={**empty_state(),'files':{'example.json':'{ "raw": [1, 1.0], "note": "phase" }'}}
 encoded=encode_state(state);assert decode_state(encoded)==state
 assert decode_state(json.dumps(state).encode())==state
 value=json.loads(encoded);value['sha256']='0'*64
 with pytest.raises(ValueError):decode_state(json.dumps(value).encode())

def test_decoder_rejects_expansion_bomb_and_unknown_schema():
 from qfault.hosted_codec import decode_state
 import base64,zlib,json
 for envelope in [{'schema_version':999},{'schema_version':2,'encoding':'zlib-base64','expanded_bytes':33554433,'sha256':'0'*64,'payload':base64.b64encode(zlib.compress(b'x'*100)).decode()}]:
  with pytest.raises(ValueError):decode_state(json.dumps(envelope).encode())

def test_global_busy_and_resource_refusal_spend_no_session_allowance():
 from tests.test_hosting import client,fixture
 from qfault.hosted_admission import Admission
 storage=MemoryState();app=client(storage);app.post('/api/hosted-session',json={})
 admission=Admission(storage.admission_state);lease=admission.acquire(100)
 assert app.post('/api/lab/recoveries',json=fixture('budget')).status_code==503
 assert app.get('/api/session').json()['used_operations']==0
 admission.release(lease)
 body=fixture('recovery');body['max_shots']=300000
 assert app.post('/api/lab/recoveries',json=body).status_code==422
 assert app.get('/api/session').json()['used_operations']==0
