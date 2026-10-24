"""Actual Chromium/Aer judge journey; only failure-injection checks may stub errors."""
import argparse
import json
import time
from urllib.parse import urlsplit
from pathlib import Path
from playwright.sync_api import expect,sync_playwright
from qfault.storage import verify_export


def run(base,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        context=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce',accept_downloads=True)
        page=context.new_page();errors=[];posts=[];began=time.monotonic()
        def response_seen(response):
            if '/api/' in response.url:
                with (out/'api-timing.jsonl').open('a') as stream:stream.write(json.dumps({'path':urlsplit(response.url).path,'status':response.status,'elapsed_seconds':time.monotonic()-began})+'\n')
        page.on('response',response_seen)
        def page_error(error):
            errors.append(str(error));(out/'page-errors.json').write_text(json.dumps(errors))
        page.on('pageerror',page_error)
        page.on('request',lambda request:posts.append({'url':request.url,'body':request.post_data_json})
                if request.method=='POST' and '/api/lab/' in request.url else None)
        def await_outcome(key,timeout):
            outcome=page.get_by_test_id('outcome-'+key)
            until=time.monotonic()+timeout/1000;lookups=0;last_lookup=0
            while time.monotonic()<until:
                if outcome.is_visible():return outcome
                if errors:raise AssertionError(errors)
                recover=page.get_by_role('button',name='Recover existing operation',exact=True)
                if recover.is_visible() and recover.is_enabled() and lookups<3 and time.monotonic()-last_lookup>5:
                    lookups+=1;last_lookup=time.monotonic();recover.click() # Existing operation lookup only; never POST a computation.
                elif page.locator('.guided-error').is_visible():raise AssertionError(page.locator('.guided-error').inner_text())
                page.wait_for_timeout(1000)
            raise AssertionError('No outcome after bounded operation lookup: '+key)
        page.goto(base)
        expect(page.locator('[data-research="measured-recovery"]')).to_contain_text('9.6% fewer shots')
        expect(page.get_by_role('button',name='Guided demo',exact=True).first).to_be_visible(timeout=5000)
        page.get_by_role('button',name='Guided demo',exact=True).first.click()
        expect(page.get_by_test_id('guided-demo')).to_be_visible()
        expect(page.get_by_text('QASMBench QRNG reference',exact=True).first).to_be_visible()
        expect(page.get_by_role('button',name='Stage 3: Complementary evidence')).to_be_disabled()
        page.get_by_role('button',name='Start with Z measurements').click()
        expect(page.get_by_role('button',name='Run Z-only measurement')).to_be_enabled()
        before=len([x for x in posts if x['url'].endswith('/investigations')])
        page.get_by_role('button',name='Run Z-only measurement').evaluate('(button)=>{button.click();button.click()}')
        z=await_outcome('z',120000)
        assert len([x for x in posts if x['url'].endswith('/investigations')])==before+1
        assert 'NO_SIGNIFICANT_DISCREPANCY' in z.inner_text()
        page.get_by_role('button',name='Add complementary evidence').click()
        page.get_by_role('button',name='Run complementary measurement').click()
        phase=await_outcome('phase',120000)
        assert 'SIGNIFICANT_DISCREPANCY' in phase.inner_text()
        page.screenshot(path=str(out/'phase.png'),full_page=True)
        page.get_by_role('button',name='Inspect bounded edits').click()
        expect(page.get_by_test_id('candidate-preview')).to_be_visible()
        page.get_by_role('button',name='Use these limits for fresh verification').click()
        page.get_by_role('button',name='Screen edits and freshly verify').click()
        recovery=await_outcome('recovery',180000)
        assert 'VERIFIED_UNDER_DECLARED_CONTRACT' in recovery.inner_text()
        first_id=recovery.get_attribute('data-experiment-id')
        page.screenshot(path=str(out/'recovery.png'),full_page=True)
        page.get_by_role('button',name='Inspect and export evidence').click()
        page.get_by_role('button',name='Check stored report integrity').click()
        expect(page.get_by_test_id('integrity-result')).to_contain_text('Stored hashes verified')
        with page.expect_download() as download:
            page.get_by_role('link',name='Download recovery report').click()
        path=out/'guided-recovery-report.json';download.value.save_as(path)
        report=json.loads(path.read_bytes());assert verify_export(report)['valid']
        assert report['investigation']['experiment_id']==first_id
        assert report['investigation']['circuit']['import_provenance']['format']=='qasm2-v1'
        page.get_by_role('button',name='Inspect Experiment History →',exact=True).click()
        expect(page.locator('#workspace-main .recent-list button').filter(has_text=first_id)).to_be_visible(timeout=5000)
        page.get_by_role('link',name='Guided demo',exact=True).click()
        expect(page.get_by_test_id('guide-preserved-records')).to_contain_text(first_id)
        page.reload();expect(page.get_by_test_id('guide-preserved-records')).to_contain_text(first_id)
        page.get_by_role('button',name='Replay with the same seed').click()
        expect(page.get_by_test_id('replay-result')).to_be_visible(timeout=180000)
        replay_id=page.get_by_test_id('replay-result').get_attribute('data-experiment-id')
        assert replay_id!=first_id
        replay=context.request.get(base+'/api/experiments/'+replay_id,max_retries=2).json()
        assert replay['replay']['source_experiment_id']==first_id and replay['replay']['semantics']=='deterministic_replay'
        for label,key,status in [('Noise-control abstention','noise','NOISE_CONTROL_ABSTENTION'),
                                 ('Insufficient budget','budget','INSUFFICIENT_BUDGET')]:
            page.get_by_role('button',name=label,exact=True).click()
            page.get_by_role('button',name='Run '+label.lower(),exact=True).click()
            outcome=await_outcome(key,120000)
            assert status in outcome.inner_text()
            if key=='budget':assert '0 shots' in outcome.inner_text()
            page.screenshot(path=str(out/(key+'.png')),full_page=True)
        page.get_by_role('button',name='Main phase investigation',exact=True).click()
        for width in (390,375,360):
            page.set_viewport_size({'width':width,'height':900})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),f'overflow at {width}'
            page.screenshot(path=str(out/f'mobile-{width}.png'),full_page=True)
        assert not errors,errors
        summary={'passed':True,'recovery_id':first_id,'replay_id':replay_id,'download_verified':True,
            'actual_posts':len(posts),'mobile_widths':[390,375,360],'page_errors':errors}
        (out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))
        browser.close()
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--base',default='http://127.0.0.1:8001');parser.add_argument('--out',required=True)
    args=parser.parse_args();run(args.base.rstrip('/'),args.out)


if __name__=='__main__':main()
