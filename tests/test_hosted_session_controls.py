import io,json,zipfile,time
from tests.test_hosting import MemoryState,client,fixture

def test_quota_export_all_preserves_reports_and_verifies_complete_membership():
 from qfault.session_export import verify_session_export
 store=MemoryState();a=client(store);a.post('/api/hosted-session',json={})
 ids=[a.post('/api/lab/recoveries',json=fixture('budget')).json()['experiment_id'] for _ in range(2)]
 info=a.get('/api/session').json();assert info['remaining_operations']==62
 export=a.get('/api/session/export');assert export.status_code==200
 checked=verify_session_export(export.content);assert checked['valid'] and set(checked['experiment_ids'])==set(ids)
 assert client(store).get('/api/session/export').status_code==200
 stream=io.BytesIO()
 with zipfile.ZipFile(io.BytesIO(export.content)) as src,zipfile.ZipFile(stream,'w') as dest:
  for name in src.namelist():
   if name!='reports/'+ids[0]+'.json':dest.writestr(name,src.read(name))
 assert not verify_session_export(stream.getvalue())['valid']

def test_delete_requires_confirmation_is_private_and_fences_stale_save():
 store=MemoryState();a=client(store);a.post('/api/lab/recoveries',json=fixture('budget'))
 sid=next(iter(store.rows));old,old_etag=store.read(sid)
 assert a.post('/api/session/delete',json={}).status_code==422
 store.rows[sid][0]['lease_until']=time.time()+10
 assert a.post('/api/session/delete',json={'confirm':'DELETE MY SESSION DATA'}).status_code==409
 store.rows[sid][0]['lease_until']=0
 assert a.post('/api/session/delete',json={'confirm':'DELETE MY SESSION DATA'}).status_code==200
 assert store.rows[sid][0]['deleted_at'] and store.rows[sid][0]['files']=={}
 from qfault.hosting import Conflict
 import pytest
 with pytest.raises(Conflict):store.write(sid,old,old_etag)

def test_prospective_retention_purges_expired_data_but_preserves_legacy():
 store=MemoryState();a=client(store);a.post('/api/lab/recoveries',json=fixture('budget'))
 sid=next(iter(store.rows));state,_=store.rows[sid];assert state['retention_expires_at']>time.time()
 state['retention_expires_at']=1
 assert a.get('/api/session').status_code==410 and store.rows[sid][0]['files']=={}
 b=client(store);b.post('/api/lab/recoveries',json=fixture('budget'))
 other=next(k for k in store.rows if k!=sid);legacy=store.rows[other][0];legacy.pop('retention_expires_at');legacy.pop('retention_policy')
 assert b.get('/api/session').status_code==200 and legacy['files']

def test_blind_export_all_excludes_hidden_setup_and_corrupt_record_refuses_complete():
 from qfault.session_export import verify_session_export
 store=MemoryState();a=client(store)
 result=a.post('/api/challenges',json={'seed':91737}).json();cid=result['challenge_id']
 response=a.get('/api/session/export');assert response.status_code==200
 assert cid in verify_session_export(response.content)['report_ids']
 with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
  report=json.loads(archive.read('reports/'+cid+'.json'))
  assert 'evaluation_truth' not in json.dumps(report) and report['state']=='OBSERVED'
 eid=a.post('/api/lab/recoveries',json=fixture('budget')).json()['experiment_id']
 sid=next(iter(store.rows));store.rows[sid][0]['files'][eid+'/manifest.json']='{}'
 assert a.get('/api/session/export').status_code==409

def test_operator_cleanup_dryrun_apply_legacy_and_active_guards():
 from qfault.hosted_retention import cleanup
 store=MemoryState()
 for sid,extra in [('a'*64,{'retention_policy':'prospective-90d-v1','retention_expires_at':1}),('b'*64,{}),('c'*64,{'retention_policy':'prospective-90d-v1','retention_expires_at':1,'lease_until':1000})]:
  store.write(sid,{'schema_version':1,'operations':1,'lease_until':0,'files':{'report.json':'{}'},**extra},None)
 assert cleanup(store,['a'*64,'b'*64,'c'*64],now=100)['eligible']==1
 assert store.read('a'*64)[0]['files']
 assert cleanup(store,['a'*64,'b'*64,'c'*64],apply=True,now=100)['purged']==1
 assert store.read('b'*64)[0]['files'] and store.read('c'*64)[0]['files']

def test_lost_delete_response_can_open_new_session_only_after_tombstone():
 store=MemoryState();a=client(store);a.post('/api/lab/recoveries',json=fixture('budget'))
 import httpx
 cookies=httpx.Cookies(a.cookies);assert a.post('/api/hosted-session',json={'reset':True}).status_code==409
 assert a.post('/api/hosted-session',json={'reset':1}).status_code==422
 assert a.post('/api/session/delete',json={'confirm':'DELETE MY SESSION DATA'}).status_code==200
 a.cookies.update(cookies) # Deliberately model losing the cookie-expiry response.
 assert a.get('/api/session').status_code==410
 assert a.post('/api/hosted-session',json={'reset':True}).status_code==200
 assert a.get('/api/session').json()['remaining_operations']==64
