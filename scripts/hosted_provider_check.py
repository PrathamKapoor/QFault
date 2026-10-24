"""Tiny disposable private-provider probe; never modifies an existing user session."""
import argparse,json,os,secrets,time
from pathlib import Path
from qfault.hosting import BlobState,empty_state,Conflict
from qfault.hosted_admission import Admission,Busy
from qfault.hosted_retention import tombstone

def run(report,environment,out):
    # A CLI-pulled ignored environment is read into this process only.
    for line in Path(environment).read_text().splitlines():
        key,sep,value=line.partition('=')
        if sep and key=='BLOB_READ_WRITE_TOKEN':os.environ[key]=json.loads(value) if value.startswith('"') else value
    storage=BlobState();request=storage.request;metrics=[]
    def measured(method,url,body=None,headers=None,limit=33554432):
        began=time.perf_counter();data=None;failed=True
        try:
            data,meta=request(method,url,body,headers,limit);failed=False;return data,meta
        finally:metrics.append({'method':method,'written_bytes':len(body or b''),'read_bytes':len(data or b''),'seconds':time.perf_counter()-began,'failed':failed})
    storage.request=measured;raw=Path(report).read_text();rows=[]
    for count in (1,4):
        sid=secrets.token_hex(32);state={**empty_state(),'files':{f'profile_{i}.json':raw for i in range(count)}}
        start=len(metrics);began=time.perf_counter();etag=storage.write(sid,state,None);loaded,current=storage.read(sid)
        assert loaded==state and current==etag
        stale=False
        try:storage.write(sid,state,'not-the-current-etag')
        except Conflict:stale=True
        assert stale
        row={'copied_reports':count,'end_to_end_seconds':time.perf_counter()-began,'transport':metrics[start:],'exact_roundtrip':True,'stale_writer_rejected':True}
        storage.write(sid,tombstone(state,'disposable-provider-probe'),current);rows.append(row)
    key='probe-admission-'+secrets.token_hex(16);gate=Admission(storage,key);other=Admission(storage,key);lease=gate.acquire(128)
    try:other.acquire(128);raise AssertionError('second admission allowed')
    except Busy:pass
    gate.release(lease);lease=other.acquire(128);other.release(lease)
    state,etag=storage.read(key);storage.write(key,tombstone(state,'disposable-provider-probe'),etag)
    proof={'passed':True,'scope':'Actual private Blob compressed snapshots/CAS and isolated admission namespace, not production stress or new scientific data','profiles':rows,'independent_admission_busy_release':True}
    with Path(out).open('x') as stream:json.dump(proof,stream,indent=2)
    print(json.dumps({'passed':True,'profiles':[{k:v for k,v in r.items() if k!='transport'} for r in rows]}))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--report',required=True);p.add_argument('--environment',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    try:run(a.report,a.environment,a.out)
    except Exception as exc:print(json.dumps({'passed':False,'error_type':type(exc).__name__,'detail':str(exc).splitlines()[0][:200]}));raise SystemExit(1)
