"""Real browser/API boundary checks for the existing shell's challenge view."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from qfault.storage import verify_export

PRIVATE={'evaluation_truth','noise_configuration','input_digest','scenario','mutation','seed','selection_seed','candidate','circuit_id'}


def private_absent(value):
    if isinstance(value,dict):
        assert not PRIVATE.intersection(value)
        for v in value.values():private_absent(v)
    elif isinstance(value,list):
        for v in value:private_absent(v)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    root=Path(args.out);root.mkdir(parents=True,exist_ok=False);errors=[];console=[];rows=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        context=browser.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce',accept_downloads=True)
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('console',lambda m:console.append(m.text) if m.type=='error' else None)
        page.goto('http://127.0.0.1:8000/#/workbench')
        page.get_by_role('link',name='Blind Challenge',exact=True).click()
        expect(page.get_by_role('heading',name='Blind quantum investigation.')).to_be_focused()
        page.screenshot(path=str(root/'challenge-configuration.png'),full_page=True)
        for mode in ['measurement_only','simulator_assisted']:
            page.goto('http://127.0.0.1:8000/#/challenge')
            page.get_by_label('Diagnostic capabilities').select_option(mode)
            if mode=='simulator_assisted':page.get_by_label('Recovery',exact=True).select_option('true')
            with page.expect_response(lambda r:r.url.endswith('/api/challenges') and r.request.method=='POST') as started:
                page.get_by_role('button',name='Start Blind Challenge').click()
            r=started.value.json();assert started.value.status==201;private_absent(r)
            cid=r['challenge_id'];expect(page).to_have_url('http://127.0.0.1:8000/#/challenges/'+cid)
            expect(page.get_by_role('button',name='Run diagnosis')).to_be_visible()
            page.screenshot(path=str(root/(mode+'-observed.png')),full_page=True)
            page.get_by_role('button',name='Run diagnosis').click()
            expect(page.get_by_role('button',name='Freeze prediction')).to_be_enabled()
            before=(context.request.get('http://127.0.0.1:8000/api/challenges/'+cid+'/report')).json()
            private_absent(before);assert verify_export(before)['valid']
            expect(page.get_by_role('heading',name='Measurement ledger')).to_be_visible()
            records=before['documents']['observed']['measurements']+before['documents']['diagnosed']['diagnostic_measurements']
            assert sum(r['executed_shots'] for r in records)==before['documents']['diagnosed']['cost']['shots']
            with page.expect_download() as download:page.get_by_role('link',name='Export current record').click()
            download.value.save_as(root/(mode+'-pre-reveal.json'))
            assert verify_export(json.loads((root/(mode+'-pre-reveal.json')).read_bytes()))['valid']
            page.get_by_role('button',name='Freeze prediction').focus();page.keyboard.press('Enter')
            expect(page.get_by_role('button',name='Reveal evaluator truth')).to_be_enabled()
            page.reload();expect(page.get_by_role('button',name='Reveal evaluator truth')).to_be_visible()
            page.screenshot(path=str(root/(mode+'-frozen.png')),full_page=True)
            page.get_by_role('button',name='Reveal evaluator truth').click()
            expect(page.get_by_role('heading',name='Evaluator truth · revealed after freeze')).to_be_visible()
            exported=context.request.get('http://127.0.0.1:8000/api/challenges/'+cid+'/report').json()
            assert verify_export(exported)['valid'];assert exported['state']=='REVEALED'
            (root/(mode+'-revealed.json')).write_text(json.dumps(exported,indent=2))
            page.screenshot(path=str(root/(mode+'-revealed.png')),full_page=True)
            page.reload();expect(page.get_by_role('heading',name='Evaluator truth · revealed after freeze')).to_be_visible()
            rows.append({'mode':mode,'challenge_id':cid,'comparison':exported['documents']['reveal']['comparison'],'verification':verify_export(exported)})
            page.get_by_role('button',name='Replay recorded challenge').click()
            expect(page.get_by_role('button',name='Run diagnosis')).to_be_visible()
            replay=context.request.get('http://127.0.0.1:8000/api/challenges').json()[0]
            assert replay['state']=='OBSERVED'
            page.go_back();expect(page.get_by_role('heading',name='Evaluator truth · revealed after freeze')).to_be_visible()
            page.go_forward();expect(page.get_by_role('button',name='Run diagnosis')).to_be_visible()
        # A declared deterministic test fixture exercises recovery UI. It is not
        # passed off as an unpredictable demonstration or a successful pool rate.
        fixture=context.request.post('http://127.0.0.1:8000/api/challenges',data={'seed':1,'diagnostic_mode':'simulator_assisted','recover':True}).json()
        private_absent(fixture)
        page.goto('http://127.0.0.1:8000/#/challenges/'+fixture['challenge_id'])
        page.get_by_role('button',name='Run diagnosis').click()
        expect(page.get_by_role('heading',name='Bounded recovery and independent verification')).to_be_visible()
        page.screenshot(path=str(root/'blind-recovery.png'),full_page=True)
        pre=context.request.get('http://127.0.0.1:8000/api/challenges/'+fixture['challenge_id']+'/report').json()
        private_absent(pre);assert verify_export(pre)['valid']
        assert pre['documents']['diagnosed']['recovery']['verification']['verified_status']=='VERIFIED'
        page.get_by_role('button',name='Freeze prediction').click()
        page.get_by_role('button',name='Reveal evaluator truth').click()
        expect(page.get_by_role('heading',name='Evaluator truth · revealed after freeze')).to_be_visible()
        page.set_viewport_size({'width':390,'height':844});page.goto('http://127.0.0.1:8000/#/challenge')
        expect(page.get_by_label('Circuit family')).to_be_visible()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.screenshot(path=str(root/'challenge-mobile.png'),full_page=True)
        page.get_by_label('Total shot ceiling').fill('2');page.get_by_role('button',name='Start Blind Challenge').click()
        assert not page.get_by_label('Total shot ceiling').evaluate('(e)=>e.validity.valid')
        assert not errors,errors
        assert not console,console
        browser.close()
    (root/'summary.json').write_text(json.dumps({'rows':rows,'page_errors':errors,'console_errors':console,
        'keyboard_freeze':True,'refresh':True,'history_navigation':True,'pre_reveal_export':True,'blind_verified_recovery':True,'mobile_no_overflow':True,'invalid_budget':True},indent=2))


if __name__=='__main__':main()
