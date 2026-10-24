"""Two concurrent zero-shot requests in disposable sessions; never a public load test."""
import argparse,asyncio,json,uuid
from pathlib import Path
from urllib.parse import urlsplit
from playwright.async_api import async_playwright,expect
from qfault.demo import demo_catalog

async def run(base,out):
    host=urlsplit(base)
    allowed=host.hostname=='qfault.vercel.app' or ((host.hostname or '').startswith('qfault-') and (host.hostname or '').endswith('-hex-sembly.vercel.app'))
    if host.scheme!='https' or host.username or host.port not in (None,443) or host.path not in ('','/') or host.query or host.fragment or not allowed:raise ValueError('Verified QFault HTTPS host required')
    output=Path(out)
    if output.exists():raise FileExistsError('New output path required')
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True)
        contexts=[await browser.new_context(reduced_motion='reduce') for _ in range(2)]
        pages=[await c.new_page() for c in contexts]
        async def open_page(page):
            await page.goto(base+'/#/demo');await expect(page.get_by_test_id('guided-demo')).to_be_visible(timeout=90000)
        await asyncio.gather(*(open_page(page) for page in pages))
        async def call(page,path,body=None,oid=None):
            return await page.evaluate('''async ({path,body,oid})=>{const r=await fetch(path,{...(body?{method:'POST',headers:{'Content-Type':'application/json',...(oid?{'X-QFault-Operation':oid}:{})},body:JSON.stringify(body)}:{}),signal:AbortSignal.timeout(90000)});return {status:r.status,body:await r.json()}}''',{'path':path,'body':body,'oid':oid})
        body=demo_catalog()['requests']['budget']['body'];observations=[];winner=None
        try:
            for attempt in range(2):
                before=[(await call(page,'/api/session'))['body']['used_operations'] for page in pages]
                ids=['operation_'+uuid.uuid4().hex for _ in pages]
                replies=await asyncio.gather(*(call(page,'/api/lab/recoveries',body,oid) for page,oid in zip(pages,ids)))
                statuses=[r['status'] for r in replies];observations.append({'attempt':attempt+1,'statuses':statuses})
                for reply in replies:
                    if reply['status']==201:assert reply['body']['status']=='INSUFFICIENT_BUDGET' and reply['body']['cost']['shots']==0
                if sorted(statuses)==[201,503]:
                    winner=statuses.index(201);loser=1-winner
                    detail=replies[loser]['body']['detail'].lower();assert 'busy' in detail or 'won admission' in detail,detail
                    after=[(await call(page,'/api/session'))['body']['used_operations'] for page in pages]
                    assert after[winner]==before[winner]+1 and after[loser]==before[loser]
                    break
                assert statuses==[201,201],statuses # Known completed non-overlap only; never repeat an unknown POST.
            assert winner is not None,'Requests did not overlap; overload behavior was not observed'
            page=pages[winner];other=pages[1-winner];oid=ids[winner];eid=replies[winner]['body']['experiment_id']
            used=(await call(page,'/api/session'))['body']['used_operations']
            same=await call(page,'/api/lab/recoveries',body,oid);assert same['status']==201 and same['body']['experiment_id']==eid
            different=await call(page,'/api/lab/recoveries',{**body,'seed':body['seed']+1},oid);assert different['status']==409
            assert (await call(page,'/api/session'))['body']['used_operations']==used
            assert (await call(page,'/api/operations/'+oid))['body']['result_id']==eid
            assert (await call(other,'/api/operations/'+oid))['status']==404
        finally:
            cleanup=[]
            for page in pages:
                try:cleanup.append((await call(page,'/api/session/delete',{'confirm':'DELETE MY SESSION DATA'}))['status'])
                except Exception:cleanup.append('unconfirmed')
        assert cleanup==[200,200],cleanup
        proof={'passed':True,'concurrent_attempts':observations,'overload_status':503,'unadmitted_allowance_delta':0,
               'same_id_one_result':True,'mismatch_status':409,'private_lookup_status':404,'scientific_shots':0,
               'disposable_sessions_deleted':True,'scope':'Actual public API and shared private-provider admission across two browser sessions; at most4tiny zero-shot requests, no stress test and no admin token'}
        with output.open('x') as stream:json.dump(proof,stream,indent=2)
        print(json.dumps(proof));await browser.close()
    return proof

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--base',required=True);parser.add_argument('--out',required=True);args=parser.parse_args()
    try:asyncio.run(run(args.base.rstrip('/'),args.out))
    except Exception as exc:print(json.dumps({'passed':False,'error':type(exc).__name__,'detail':(str(exc).splitlines() or ['empty assertion'])[0][:200]}));raise SystemExit(1)
