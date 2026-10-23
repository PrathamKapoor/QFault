import copy
import json
import pytest
from fastapi.testclient import TestClient


class MemoryState:
    def __init__(self): self.rows={}; self.sequence=0; self.fail=False
    def read(self,sid):
        from qfault.hosting import empty_state
        return copy.deepcopy(self.rows.get(sid,(empty_state(),None)))
    def write(self,sid,state,etag):
        from qfault.hosting import Conflict
        if self.fail: raise OSError('private storage unavailable')
        if self.rows.get(sid,(None,None))[1]!=etag: raise Conflict()
        self.sequence+=1; new=str(self.sequence)
        self.rows[sid]=(copy.deepcopy(state),new);return new


def client(storage,**kwargs):
    from qfault.hosting import HostedApp
    from qfault.api import RequestBodyLimit
    from qfault.hosted_admission import Admission
    if not hasattr(storage,'admission_state'):storage.admission_state=MemoryState()
    return TestClient(RequestBodyLimit(HostedApp(storage=storage,secret='a'*64,hosts={'public.example'},admission=Admission(storage.admission_state),**kwargs)),base_url='https://public.example')


def fixture(key):
    from qfault.demo import demo_catalog
    return demo_catalog()['requests'][key]['body']


def test_hosted_real_recovery_persists_across_instances_and_is_private():
    store=MemoryState();first=client(store)
    result=first.post('/api/lab/recoveries',json=fixture('recovery'))
    assert result.status_code==201,result.text
    run=result.json();assert run['status']=='VERIFIED_UNDER_DECLARED_CONTRACT'
    eid=run['experiment_id'];second=client(store);second.cookies.update(first.cookies)
    report=second.get(f'/api/experiments/{eid}/report')
    from qfault.storage import verify_export
    assert report.status_code==200 and verify_export(report.json())['valid']
    assert client(store).get(f'/api/experiments/{eid}').status_code==404
    assert len(second.get('/api/experiments').json())==1
    assert 'no-store' in report.headers['cache-control']
    assert first.cookies.get('__Host-qfault-session')


def test_hosted_rejects_external_origin_host_and_oversize_before_storage():
    store=MemoryState();app=client(store)
    assert app.get('/api/health',headers={'host':'evil.example'}).status_code==400
    assert app.post('/api/lab/validate',json=fixture('z'),headers={'origin':'https://evil.example'}).status_code==403
    assert app.post('/api/lab/validate',content=b' '*65537).status_code==413
    assert not store.rows
    assert app.get('/api/health').json()['hosting']['persistence']=='private Vercel Blob'


def test_storage_failure_never_returns_a_successful_result():
    store=MemoryState();store.fail=True
    response=client(store).post('/api/lab/recoveries',json=fixture('budget'))
    assert response.status_code==503 and 'private storage unavailable' not in response.text
    assert not store.rows


def test_lease_and_operation_ceiling_are_enforced():
    store=MemoryState();app=client(store)
    assert app.post('/api/lab/recoveries',json=fixture('budget')).status_code==201
    sid=next(iter(store.rows));state,etag=store.rows[sid]
    state['lease_until']=10**12
    assert app.post('/api/lab/recoveries',json=fixture('budget')).status_code==409
    state['lease_until']=0;state['operations']=64
    assert app.post('/api/lab/recoveries',json=fixture('budget')).status_code==429


@pytest.mark.parametrize('files',[{'../escape.json':'{}'},{'/escape.json':'{}'},{'a/../escape.json':'{}'},{'a.json':[]},{'a\\escape.json':'{}'}])
def test_snapshot_rejects_unsafe_members(files,tmp_path):
    from qfault.hosting import restore
    with pytest.raises(ValueError):restore(tmp_path,files)


def test_blob_transport_requires_current_etag_and_conditional_writes():
    from qfault.hosting import BlobState,Conflict
    calls=[]
    def request(method,url,body=None,headers=None,limit=None):
        calls.append((method,url,headers))
        if method=='PUT':raise Conflict()
        if 'blob.vercel-storage.com' in url and 'url=' in url:
            return json.dumps({'url':'https://abc.private.blob.vercel-storage.com/sessions/id.json','etag':'new'}).encode(),{}
        return b'{}',{'etag':'stale'}
    blob=BlobState('vercel_blob_rw_abc_test',request=request)
    with pytest.raises(OSError):blob.read('a'*64)
    with pytest.raises(Conflict):blob.write('a'*64,{},'etag-expected')
    assert calls[-1][2]['x-if-match']=='etag-expected'


def test_private_reads_explicitly_bypass_provider_cdn_after_overwrite():
    from qfault.hosting import BlobState,empty_state
    from urllib.parse import parse_qs,urlsplit
    state=empty_state()
    def request(method,url,body=None,headers=None,limit=None):
        if 'url=' in url:return json.dumps({'url':'https://abc.private.blob.vercel-storage.com/sessions/test.json','etag':'latest'}).encode(),{}
        if parse_qs(urlsplit(url).query).get('cache')==['0']:return json.dumps(state).encode(),{'etag':'latest'}
        return json.dumps(state).encode(),{'etag':'old-cached'}
    assert BlobState('unused',request=request).read('a'*64)==(state,'latest')


def test_bootstrap_cookie_precedes_workbench_and_reads_never_replace_it():
    store=MemoryState();app=client(store)
    assert 'set-cookie' not in app.get('/api/research').headers
    boot=app.post('/api/hosted-session',json={})
    assert boot.status_code==200 and app.cookies.get('__Host-qfault-session')
    assert 'set-cookie' not in app.get('/api/health').headers
    assert not store.rows


def test_blind_lifecycle_restores_private_state_across_function_instances():
    from qfault.storage import verify_export
    store=MemoryState();app=client(store)
    started=app.post('/api/challenges',json={'seed':91737}).json()
    path='/api/challenges/'+started['challenge_id']
    assert app.post(path+'/reveal').status_code==409
    assert app.post(path+'/diagnose').status_code==200
    assert app.post(path+'/freeze').json()['state']=='FROZEN'
    fresh=client(store);fresh.cookies.update(app.cookies)
    assert fresh.get(path).json()['state']=='FROZEN'
    assert fresh.post(path+'/reveal').json()['state']=='REVEALED'
    assert verify_export(fresh.get(path+'/report').json())['valid']
    assert client(store).get(path).status_code==404


def test_expired_lease_keeps_prior_records_and_forged_cookie_has_no_access():
    store=MemoryState();app=client(store)
    first=app.post('/api/lab/recoveries',json=fixture('budget')).json();eid=first['experiment_id']
    sid=next(iter(store.rows));store.rows[sid][0]['lease_until']=1
    assert app.post('/api/lab/recoveries',json=fixture('budget')).status_code==201
    assert len(app.get('/api/experiments').json())==2
    forged=client(store);cookie=app.cookies.get('__Host-qfault-session')
    forged.cookies.set('__Host-qfault-session',cookie[:-1]+('0' if cookie[-1]!='0' else '1'),domain='public.example',path='/')
    assert forged.get('/api/experiments/'+eid).status_code==404


def test_commit_conflict_cannot_return_verified_or_overwrite_new_owner():
    class ConflictOnCommit(MemoryState):
        def write(self,sid,state,etag):
            if etag is not None:
                from qfault.hosting import Conflict
                self.rows[sid]=(self.rows[sid][0],'new-owner');raise Conflict()
            return super().write(sid,state,etag)
    store=ConflictOnCommit()
    response=client(store).post('/api/lab/recoveries',json=fixture('budget'))
    assert response.status_code==409
    assert next(iter(store.rows.values()))[1]=='new-owner'
