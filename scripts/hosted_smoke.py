"""Real public Vercel/Aer checks; no provider or session secrets are persisted."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
from qfault.demo import demo_catalog
from qfault.storage import verify_export
from scripts.guided_demo_e2e import run as guided


def run(base,out):
    if urlsplit(base).scheme!='https':raise ValueError('Hosted checks require HTTPS')
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    with sync_playwright() as p:
        browser=p.chromium.launch();first=browser.new_context();second=browser.new_context()
        health=first.request.get(base+'/api/health',timeout=120000)
        assert health.status==200,health.text()
        assert health.json()['aer']['version']=='0.17.2',health.text()
        bootstrap=first.request.post(base+'/api/hosted-session',data={})
        assert bootstrap.status==200,bootstrap.text()
        cookies=first.cookies()
        assert any(c['name']=='__Host-qfault-session' and c['secure'] and c['httpOnly'] for c in cookies)
        body=demo_catalog()['requests']['budget']['body']
        response=first.request.post(base+'/api/lab/recoveries',data=body,timeout=120000)
        assert response.status==201,response.text()
        record=response.json();eid=record['experiment_id']
        assert record['status']=='INSUFFICIENT_BUDGET' and record['cost']['shots']==0
        report=first.request.get(base+'/api/experiments/'+eid+'/report',timeout=120000)
        assert report.status==200 and verify_export(report.json())['valid']
        assert 'no-store' in report.headers['cache-control']
        assert second.request.get(base+'/api/experiments/'+eid).status==404
        assert second.request.get(base+'/api/experiments').json()==[]
        # A fresh browser context can restore its own record using only its cookie.
        first.close();restored=browser.new_context();restored.add_cookies(cookies)
        loaded=restored.request.get(base+'/api/experiments/'+eid+'/report')
        assert loaded.status==200 and verify_export(loaded.json())['valid']
        replay=restored.request.post(base+'/api/lab/recoveries/'+eid+'/replay',data={},timeout=120000)
        assert replay.status==201,replay.text()
        assert replay.json()['experiment_id']!=eid and replay.json()['replay']['source_experiment_id']==eid
        count=len(restored.request.get(base+'/api/experiments').json())
        assert restored.request.post(base+'/api/lab/recoveries',data=body,headers={'Origin':'https://untrusted.example'}).status==403
        assert restored.request.post(base+'/api/lab/recoveries',data=' '*65537,headers={'Content-Type':'application/json'}).status==413
        assert len(restored.request.get(base+'/api/experiments').json())==count
        challenge=restored.request.post(base+'/api/challenges',data={'seed':91737},timeout=120000)
        assert challenge.status==201,challenge.text()
        cid=challenge.json()['challenge_id'];path=base+'/api/challenges/'+cid
        assert restored.request.post(path+'/reveal',timeout=120000).status==409
        assert restored.request.post(path+'/diagnose',timeout=120000).status==200
        assert restored.request.post(path+'/freeze',timeout=120000).json()['state']=='FROZEN'
        assert second.request.get(path).status==404
        assert restored.request.post(path+'/reveal',timeout=120000).json()['state']=='REVEALED'
        assert verify_export(restored.request.get(path+'/report').json())['valid']
        proof={'public_api':True,'aer':'0.17.2','private_history':True,'cookie_restore':True,
            'independent_export_verification':True,'distinct_replay':True,'same_origin':True,
            'actual_body_limit':True,'blind_freeze_reveal':True,'budget_id':eid,'challenge_id':cid,
            'scope':'Actual remote provider/API/engine; browser-context restore, not a forced provider restart'}
        browser.close()
    (out/'api-summary.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
    result=guided(base,out/'guided')
    (out/'summary.json').write_text(json.dumps({'passed':True,'base':base,'api':proof,'guided':result},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--base',required=True);parser.add_argument('--out',required=True)
    args=parser.parse_args();existed=Path(args.out).exists()
    try:run(args.base.rstrip('/'),args.out)
    except Exception as exc:
        # Playwright call logs may include the browser capability cookie. Retain
        # the exact first error line, not credential-bearing request headers.
        failure={'passed':False,'error_type':type(exc).__name__,'detail':str(exc).splitlines()[0][:400],
                 'retry_semantics':'No POST is automatically retried; inspect history for unknown completion.'}
        folder=Path(args.out)
        if not existed and folder.is_dir():
            with (folder/'failure.json').open('x',encoding='utf8') as stream:json.dump(failure,stream,indent=2)
        print(json.dumps(failure));raise SystemExit(1)
