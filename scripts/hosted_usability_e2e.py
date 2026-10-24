"""Actual hosted UI/provider/Aer journey, with one deliberately lost response."""
import argparse,json,time
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from qfault.session_export import verify_session_export
from qfault.storage import verify_export

def run(base,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        context=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce',accept_downloads=True)
        page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(base);expect(page.get_by_role('button',name='Run the guided demo',exact=True)).to_be_visible()
        page.get_by_role('button',name='Run the guided demo',exact=True).click()
        expect(page.get_by_test_id('guided-demo')).to_be_visible(timeout=90000)
        assert 'REAL LOCAL MEASUREMENTS' not in page.get_by_test_id('guided-demo').inner_text()
        page.get_by_label('Guided circuit',exact=True).select_option('cat')
        expect(page.get_by_text('QASMBench entangled cat reference',exact=True)).to_be_visible()
        page.get_by_role('button',name='Start with Z measurements').click()
        transport_errors=[]
        def completed_operation_id():
            saved=json.loads(page.evaluate("sessionStorage.getItem('qfault-guided-demo-v1-cat')"));oid=saved['pending']['operationId']
            for _ in range(3):
                value=page.evaluate('''async id=>{const r=await fetch('/api/operations/'+id,{signal:AbortSignal.timeout(20000)});return {status:r.status,body:await r.json()}}''',oid)
                if value['status']==200 and value['body']['state']=='COMPLETED':return value['body']['result_id']
                page.wait_for_timeout(1000)
            raise AssertionError('Original operation is not durably completed; no POST was retried')
        lost=[];before_admission=[]
        page.route('**/api/lab/investigations',lambda route:before_admission.append(route),times=1)
        page.get_by_role('button',name='Run Z-only measurement').click()
        until=time.monotonic()+30
        while not before_admission and time.monotonic()<until:page.wait_for_timeout(100)
        assert before_admission,'The original request was not intercepted'
        page.get_by_role('button',name='Recover existing operation',exact=True).click()
        expect(page.get_by_text('No durable operation is visible in this browser session yet.',exact=False)).to_be_visible(timeout=30000)
        used=page.evaluate('async()=>{const r=await fetch("/api/session");return (await r.json()).used_operations}')
        assert used==0,'Unadmitted request must not spend allowance'
        try:
            response=before_admission[0].fetch(timeout=120000);assert response.status==201
            lost.append(response.json()['experiment_id'])
        except Exception as exc:
            transport_errors.append({'stage':'z','type':type(exc).__name__,'detail':(str(exc).splitlines() or ['empty'])[0][:200]})
            lost.append(completed_operation_id())
        before_admission[0].abort('failed')
        expect(page.get_by_text('Completion unknown',exact=True)).to_be_visible(timeout=120000)
        page.reload();expect(page.get_by_text('Completion unknown',exact=True)).to_be_visible(timeout=90000)
        page.get_by_role('button',name='Recover existing operation',exact=True).click()
        z=page.get_by_test_id('outcome-z');expect(z).to_be_visible(timeout=90000)
        assert z.get_attribute('data-experiment-id')==lost[0]
        assert 'NO_SIGNIFICANT_DISCREPANCY' in z.inner_text()
        page.get_by_role('button',name='Add complementary evidence').click()
        held=[];phase_mode=['held']
        def hold_completed_response(route):
            try:
                response=route.fetch(timeout=120000);assert response.status==201
                held.append(response.json()['experiment_id'])
                # Intentionally do not fulfill the browser response. Server work is done.
            except Exception as exc:
                transport_errors.append({'stage':'phase','type':type(exc).__name__,'detail':(str(exc).splitlines() or ['empty'])[0][:200]})
                phase_mode[0]='lost_in_transport';held.append(None);route.abort('failed')
        page.route('**/api/lab/investigations',hold_completed_response,times=1)
        page.get_by_role('button',name='Run complementary measurement').click()
        until=time.monotonic()+90
        while not held and time.monotonic()<until:page.wait_for_timeout(100)
        assert held,'No durable phase result was observed'
        if held[0] is None:held[0]=completed_operation_id()
        expect(page.get_by_test_id('outcome-phase')).to_have_count(0)
        page.get_by_role('button',name='Recover existing operation',exact=True).click()
        expect(page.get_by_test_id('outcome-phase')).to_contain_text('SIGNIFICANT_DISCREPANCY',timeout=90000)
        assert page.get_by_test_id('outcome-phase').get_attribute('data-experiment-id')==held[0]
        page.get_by_role('button',name='Inspect bounded edits').click()
        page.get_by_role('button',name='Use these limits for fresh verification').click()
        page.get_by_role('button',name='Screen edits and freshly verify').click()
        recovery=page.get_by_test_id('outcome-recovery');expect(recovery).to_contain_text('VERIFIED_UNDER_DECLARED_CONTRACT',timeout=240000)
        eid=recovery.get_attribute('data-experiment-id')
        summary=recovery.get_by_test_id('result-summary');expect(summary).to_contain_text('Selected edit:')
        assert 'fresh verification shots' in summary.inner_text()
        expect(page.locator('.history-label span')).to_have_text('3',timeout=90000)
        # Native browser fetch uses its private cookie; no capability is exported.
        value=page.evaluate('async id=>{const r=await fetch("/api/experiments/"+id+"/report");return {status:r.status,raw:await r.text()}}',eid)
        assert value['status']==200,f'report HTTP{value["status"]}'
        (out/'entangling-report.json').write_text(value['raw'])
        value['body']=json.loads(value['raw']);checked=verify_export(value['body'])
        assert checked['valid'],checked.get('errors')
        for width in (390,375,360):
            page.set_viewport_size({'width':width,'height':900})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),f'overflow{width}'
            page.screenshot(path=str(out/f'entangling-{width}.png'),full_page=True)
        assert page.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches')
        page.get_by_text('Session allowance, export, recovery and deletion',exact=False).click()
        with page.expect_download() as download:page.get_by_role('link',name='Export all accessible reports').click()
        archive=out/'session-reports.zip';download.value.save_as(archive)
        exported=verify_session_export(archive.read_bytes());assert exported['valid'] and len(exported['experiment_ids'])==3
        other=browser.new_context();other_page=other.new_page();other_page.goto(base+'/#/demo')
        expect(other_page.get_by_test_id('guided-demo')).to_be_visible(timeout=90000)
        isolated=other_page.evaluate('async id=>(await fetch("/api/experiments/"+id)).status',eid);assert isolated==404
        page.get_by_label('I understand the permanent loss and have exported reports I need.').check()
        with page.expect_navigation(wait_until='domcontentloaded',timeout=90000):
            page.get_by_role('button',name='Permanently delete this session data',exact=True).click()
        expect(page.get_by_test_id('guided-demo')).to_be_visible(timeout=90000)
        expect(page.get_by_test_id('outcome-z')).to_have_count(0)
        info=page.evaluate('async()=>{const r=await fetch("/api/session");return await r.json()}')
        assert info['remaining_operations']==64
        assert page.evaluate('async id=>(await fetch("/api/experiments/"+id)).status',eid)==404
        assert not errors,errors
        proof={'passed':True,'example':'qasmbench-cat-phase-v1','lost_response_recovered_same_id':lost[0],
               'stalled_response_recovered_same_id':held[0],'phase_response_mode':phase_mode[0],'transport_errors':transport_errors,'recovery_id':eid,'cost':value['body']['investigation']['cost'],'history_count':3,'unadmitted_lookup_retains_pending_without_cost':True,
               'complete_export_verified':True,'isolated':True,'disposable_session_deleted':True,
               'mobile_widths':[390,375,360],'reduced_motion':True,'page_errors':errors,
               'scope':'Actual browser/provider/Aer. Only one response was deliberately dropped AFTER durable completion; no success response was mocked.'}
        (out/'summary.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof));browser.close()
    return proof

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    try:run(a.base.rstrip('/'),a.out)
    except Exception as exc:print(json.dumps({'passed':False,'error':type(exc).__name__,'detail':(str(exc).splitlines() or [type(exc).__name__])[0][:300]}));raise SystemExit(1)
