import copy
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from tests.test_hosting import MemoryState,client,fixture

OID='operation_'+'a'*32
def test_durable_same_request_returns_one_original_and_mismatch_rejected():
 store=MemoryState();a=client(store);a.post('/api/hosted-session',json={})
 h={'X-QFault-Operation':OID};body=fixture('budget')
 r=a.post('/api/lab/recoveries',json=body,headers=h);assert r.status_code==201
 eid=r.json()['experiment_id']
 b=client(store);b.cookies.update(a.cookies)
 repeat=b.post('/api/lab/recoveries',json=body,headers=h)
 assert repeat.status_code==201 and repeat.json()['experiment_id']==eid
 assert len(b.get('/api/experiments').json())==1
 op=b.get('/api/operations/'+OID).json();assert op['state']=='COMPLETED' and op['result_id']==eid
 body['seed']+=1;assert b.post('/api/lab/recoveries',json=body,headers=h).status_code==409
 assert client(store).get('/api/operations/'+OID).status_code==404
 assert next(iter(store.rows.values()))[0]['operations']==1

def test_expired_operation_is_unknown_and_never_resubmitted():
 store=MemoryState();a=client(store);a.post('/api/lab/recoveries',json=fixture('budget'),headers={'X-QFault-Operation':OID})
 sid=next(iter(store.rows));state,etag=store.rows[sid];state['requests'][OID].update(state='RUNNING',lease_until=1);state['lease_until']=1
 response=a.post('/api/lab/recoveries',json=fixture('budget'),headers={'X-QFault-Operation':OID})
 assert response.status_code==202 and response.json()['state']=='UNKNOWN'
 assert len(a.get('/api/experiments').json())==1

def test_save_failure_retains_unknown_identity_without_duplicate_execution():
 class FailCompletion(MemoryState):
  def write(self,sid,state,etag):
   if any(v.get('state')=='COMPLETED' for v in state.get('requests',{}).values()):raise OSError('lost save')
   return super().write(sid,state,etag)
 store=FailCompletion();a=client(store);a.post('/api/hosted-session',json={})
 assert a.post('/api/lab/recoveries',json=fixture('budget'),headers={'X-QFault-Operation':OID}).status_code==503
 assert a.get('/api/operations/'+OID).json()['state']=='UNKNOWN'
 assert a.post('/api/lab/recoveries',json=fixture('budget'),headers={'X-QFault-Operation':OID}).status_code==202

def test_invalid_request_executes_nothing_and_spends_no_allowance():
 store=MemoryState();a=client(store);a.post('/api/hosted-session',json={})
 assert a.post('/api/lab/recoveries',json={'bad':True},headers={'X-QFault-Operation':OID}).status_code==422
 assert all(row[0]['operations']==0 for row in store.rows.values())

def test_two_instances_same_operation_cannot_both_execute(monkeypatch):
 import qfault.counterfactual as core
 original=core.recover;entered=threading.Event();finish=threading.Event();calls=[]
 def held(request):
  calls.append(1);entered.set();assert finish.wait(10);return original(request)
 monkeypatch.setattr(core,'recover',held)
 store=MemoryState();a=client(store);a.post('/api/hosted-session',json={})
 b=client(store);b.cookies.update(a.cookies);h={'X-QFault-Operation':OID}
 with ThreadPoolExecutor() as pool:
  first=pool.submit(a.post,'/api/lab/recoveries',json=fixture('budget'),headers=h)
  assert entered.wait(10)
  second=b.post('/api/lab/recoveries',json=fixture('budget'),headers=h)
  assert second.status_code==202 and second.json()['state']=='RUNNING'
  finish.set();assert first.result().status_code==201
 assert len(calls)==1 and len(a.get('/api/experiments').json())==1

def test_delayed_original_cannot_restore_content_after_expired_lease_deletion(monkeypatch):
 import qfault.counterfactual as core
 original=core.recover;entered=threading.Event();finish=threading.Event()
 def held(request):entered.set();assert finish.wait(10);return original(request)
 monkeypatch.setattr(core,'recover',held)
 store=MemoryState();a=client(store);a.post('/api/hosted-session',json={})
 b=client(store);b.cookies.update(a.cookies)
 with ThreadPoolExecutor() as pool:
  future=pool.submit(a.post,'/api/lab/recoveries',json=fixture('budget'),headers={'X-QFault-Operation':OID})
  assert entered.wait(10);sid=next(iter(store.rows));store.rows[sid][0]['lease_until']=1
  assert b.post('/api/session/delete',json={'confirm':'DELETE MY SESSION DATA'}).status_code==200
  finish.set();assert future.result().status_code==409
 assert store.rows[sid][0]['files']=={} and store.rows[sid][0]['deleted_at']
