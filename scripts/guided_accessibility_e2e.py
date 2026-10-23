"""Guided keyboard/mobile and explicitly labelled failure-injection browser checks."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import expect,sync_playwright


def run(base,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        checked=[]
        for width in (1440,390,375,360):
            context=browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce')
            page=context.new_page();page.goto(base)
            entry=page.get_by_role('button',name='Guided demo',exact=True).first
            expect(entry).to_be_visible(timeout=5000)
            entry.focus();page.keyboard.press('Enter')
            expect(page.get_by_test_id('guided-demo')).to_be_visible()
            button=page.get_by_role('button',name='Start with Z measurements')
            button.focus();page.keyboard.press('Enter')
            expect(page.get_by_role('button',name='Run Z-only measurement')).to_be_enabled()
            assert page.evaluate('document.activeElement.getAttribute("aria-label")')=='Current guided stage'
            page.keyboard.press('Tab')
            assert page.evaluate('document.activeElement.textContent')=='Run Z-only measurement'
            assert page.evaluate('parseFloat(getComputedStyle(document.activeElement).outlineWidth)')>=2
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),f'overflow {width}'
            page.screenshot(path=str(out/f'keyboard-{width}.png'),full_page=True)
            checked.append(width);context.close()
        context=browser.new_context(viewport={'width':1200,'height':900},reduced_motion='reduce')
        page=context.new_page();page.goto(base+'/#/demo')
        page.get_by_role('button',name='Start with Z measurements').click()
        expect(page.get_by_role('button',name='Run Z-only measurement')).to_be_enabled()
        # Error-only fault injection. Positive investigation below still reaches Aer.
        def busy(route):route.fulfill(status=409,content_type='application/json',body=json.dumps({'detail':'An investigation is already running'}))
        page.route('**/api/lab/investigations',busy)
        page.get_by_role('button',name='Run Z-only measurement').click()
        expect(page.get_by_role('alert')).to_contain_text('Server busy')
        assert page.get_by_test_id('outcome-z').count()==0
        expect(page.get_by_role('button',name='Run Z-only measurement')).to_be_enabled()
        page.unroute('**/api/lab/investigations',busy)
        page.get_by_role('button',name='Run Z-only measurement').click()
        expect(page.get_by_test_id('outcome-z')).to_be_visible(timeout=120000)
        z_id=page.get_by_test_id('outcome-z').get_attribute('data-experiment-id')
        page.get_by_role('button',name='Add complementary evidence').click()
        expect(page.get_by_role('button',name='Run complementary measurement')).to_be_enabled()
        page.route('**/api/lab/investigations',lambda route:route.abort('connectionfailed'))
        page.get_by_role('button',name='Run complementary measurement').click()
        expect(page.get_by_role('alert')).to_contain_text('Connection lost')
        expect(page.get_by_role('button',name='Noise-control abstention',exact=True)).to_be_disabled()
        page.reload()
        expect(page.get_by_text('Completion unknown',exact=True)).to_be_visible()
        expect(page.get_by_test_id('guide-preserved-records')).to_contain_text(z_id)
        expect(page.get_by_role('button',name='Start a new guide and preserve earlier records')).to_be_disabled()
        page.screenshot(path=str(out/'unknown-completion.png'),full_page=True)
        page.get_by_role('checkbox').check()
        page.get_by_role('button',name='Start a new guide and preserve earlier records').click()
        expect(page.get_by_role('button',name='Start with Z measurements')).to_be_visible()
        assert context.request.get(base+'/api/experiments/'+z_id).status==200
        page.evaluate('''(id)=>{const key='qfault-guided-demo-v1';const state=JSON.parse(sessionStorage.getItem(key));
            state.ids={z:id,phase:'experiment_'+ 'f'.repeat(32)};state.stage='z';sessionStorage.setItem(key,JSON.stringify(state))}''',z_id)
        page.reload()
        expect(page.get_by_test_id('outcome-z')).to_be_visible(timeout=5000)
        expect(page.get_by_role('alert')).to_contain_text('could not be restored')
        context.close()
        summary={'passed':True,'keyboard_mobile_widths':checked,'reduced_motion':True,
            'fault_injection':['HTTP409 only','connection abort only'],
            'real_aer_retry_id':z_id,'unknown_completion_preserves_old_record':True}
        (out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary));browser.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--base',default='http://127.0.0.1:8001');parser.add_argument('--out',required=True)
    args=parser.parse_args();run(args.base.rstrip('/'),args.out)


if __name__=='__main__':main()
