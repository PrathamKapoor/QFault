"""Real HTTP checks against the running product; explicitly not browser E2E."""
import argparse,json,re
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from qfault.storage import verify_export
from qfault.evidence import canonical,digest

def call(path,data=None):
    request=Request('http://127.0.0.1:8000'+path,data=json.dumps(data).encode() if data is not None else None,headers={'Content-Type':'application/json'})
    try:
        with urlopen(request,timeout=30) as r:return r.status,r.read(),dict(r.headers)
    except HTTPError as e:return e.code,e.read(),dict(e.headers)

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();root=Path(a.out);root.mkdir(parents=True,exist_ok=False);checks=[]
    for path in ['/api/health','/api/circuits','/api/contracts/bell/2','/api/benchmark','/api/evaluation','/api/evaluation/report']:
        status,body,_=call(path);assert status==200;checks.append({'path':path,'status':status});(root/(path.replace('/','_')+'.json')).write_bytes(body)
    status,body,_=call('/');assert status==200;html=body.decode();assets=re.findall(r'(?:src|href)="(/assets/[^"]+)"',html);assert assets
    for asset in assets:assert call(asset)[0]==200
    rows=[]
    for settings in [{'scenario':'clean'},{'scenario':'remove'},{'scenario':'readout'},{'scenario':'remove','max_shots':4096,'max_evaluations':2}]:
        status,body,_=call('/api/experiments',{'family':'bell','policy':'phase','backend':'aer','seed':613,**settings});assert status==201;result=json.loads(body);eid=result['experiment_id'];(root/(eid+'.json')).write_bytes(body)
        assert call('/api/experiments/'+eid)[0]==200
        assert json.loads(call('/api/experiments/'+eid+'/verification')[1])['valid']
        status,body,headers=call('/api/experiments/'+eid+'/report');assert status==200 and 'attachment' in headers['content-disposition'];report=json.loads(body);assert verify_export(report)['valid'];(root/(eid+'-export.json')).write_bytes(body)
        assert all(r['backend_name'].startswith('qiskit_aer.') for r in result['executions'])
        rows.append({'scenario':settings,'experiment_id':eid,'diagnosis':result['diagnosis']['category'],'recovery':result['recovery']['status'] if result['recovery'] else None,'export_valid':True,'shots':result['cost']['shots'],'report_digest':digest(report)})
    status,_,_=call('/api/experiments',{'shots':0});assert status==422;checks.append({'invalid_shots_status':status})
    status,_,_=call('/api/contracts/bell/3');assert status==422;checks.append({'invalid_contract_status':status})
    assert rows[0]['diagnosis']=='NO_SIGNIFICANT_FAILURE_DETECTED' and rows[1]['recovery']=='VERIFIED' and rows[2]['diagnosis']=='NOISE_CONSISTENT_DEGRADATION' and rows[3]['diagnosis']=='INSUFFICIENT_EVIDENCE'
    summary={'checks':checks,'production_assets':assets,'workflows':rows,'browser_e2e':'NOT TESTED BY THIS HTTP SCRIPT; run scripts.browser_e2e separately','console_render_responsive_screenshots':'NOT VERIFIED'};(root/'summary.json').write_bytes(canonical(summary));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
