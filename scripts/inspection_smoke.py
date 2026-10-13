"""Final, non-disruptive inspection smoke against the integrated local server."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
    errors=[];console=[];failed=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        context=browser.new_context(viewport={'width':1440,'height':900})
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('console',lambda m:console.append(m.text) if m.type=='error' else None)
        page.on('requestfailed',lambda r:failed.append(r.url))
        response=page.goto((__import__('os').environ.get('QFAULT_BASE_URL','http://127.0.0.1:8000') + '/'))
        expect(page.locator('[data-phase="hero"]')).to_be_attached(timeout=20000)
        expect(page.locator('.entry__stage canvas[data-engine="webgl"]')).to_be_attached(timeout=20000)
        page.wait_for_timeout(1100);page.screenshot(path=str(out/'landing-desktop.png'))
        page.get_by_role('button',name='Enter Workbench',exact=True).click()
        expect(page.get_by_role('heading',name='Quantum investigation intelligence.')).to_be_focused()
        expect(page.locator('.overview[data-ready="true"]')).to_be_attached(timeout=30000)
        page.screenshot(path=str(out/'workbench-desktop.png'),full_page=True)
        page.get_by_role('button',name='New Investigation',exact=True).first.click()
        page.get_by_label('Simulation backend').select_option('aer')
        page.get_by_label('Diagnostic policy').select_option('phase')
        page.get_by_label('Execution scenario').select_option('remove')
        with page.expect_response(lambda r:r.url.endswith('/api/experiments') and r.request.method=='POST') as run:
            page.get_by_role('button',name='Run investigation').click()
        result=run.value.json();assert run.value.status==201
        assert result['diagnosis']['category']=='LOGICAL_CIRCUIT_DEFECT'
        assert result['recovery']['status']=='VERIFIED'
        expect(page.get_by_text('Artifact hashes verified',exact=True)).to_be_visible()
        assert not errors and not console and not failed,(errors,console,failed)
        summary={'http_status':response.status,'landing_webgl':True,'workbench_loaded':True,
            'experiment_id':result['experiment_id'],'backend':'aer','recovery':'VERIFIED',
            'page_errors':errors,'console_errors':console,'failed_requests':failed}
        (out/'summary.json').write_text(json.dumps(summary,indent=2))
        browser.close()

if __name__=='__main__':main()
