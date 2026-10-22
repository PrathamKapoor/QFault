"""Actual native-import JSON/editor/Aer/recovery/export and light-surface contrast."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from scripts.judging_demo import example
from scripts.lab_e2e import paste
from qfault.storage import verify_export


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--base',default='http://127.0.0.1:8000');parser.add_argument('--out',required=True)
    args=parser.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
    circuit,_,contract=example();errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        context=browser.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce',accept_downloads=True)
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(args.base+'/#/lab')
        paste(page,'Circuit JSON',circuit);paste(page,'Contract JSON',contract)
        page.get_by_label('Backend').select_option('aer')
        with page.expect_response(lambda r:r.url.endswith('/api/lab/validate') and r.request.method=='POST') as response:
            page.get_by_role('button',name='Validate and check feasibility').click()
        assert response.value.status==200
        with page.expect_response(lambda r:r.url.endswith('/api/lab/investigations') and r.request.method=='POST') as response:
            page.get_by_role('button',name='Run investigation',exact=True).click()
        result=response.value.json();assert response.value.status==201 and result['diagnosis']['category']=='SIGNIFICANT_DISCREPANCY'
        assert result['circuit']['import_provenance']==circuit['import_provenance']
        page.screenshot(path=str(out/'native-phase.png'),full_page=True)
        page.get_by_role('button',name='Measured recovery').click()
        with page.expect_response(lambda r:r.url.endswith('/api/lab/recoveries') and r.request.method=='POST',timeout=120000) as response:
            page.get_by_role('button',name='Run measured recovery',exact=True).click()
        recovery=response.value.json();assert response.value.status==201 and recovery['status']=='VERIFIED_UNDER_DECLARED_CONTRACT'
        assert recovery['circuit']['import_provenance']==circuit['import_provenance']
        expect(page.get_by_text('verified under declared contract',exact=True).first).to_be_visible()
        with page.expect_download() as download:
            page.get_by_role('link',name='Export recovery evidence').click()
        path=out/'native-recovery-report.json';download.value.save_as(path)
        assert verify_export(json.loads(path.read_bytes()))['valid']
        page.screenshot(path=str(out/'native-recovery.png'),full_page=True)
        mobile=[]
        for width in (390,375,360):
            page.set_viewport_size({'width':width,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            page.screenshot(path=str(out/f'native-recovery-{width}.png'),full_page=True)
            mobile.append(width)
        page.goto(args.base+'/#/workbench')
        expect(page.locator('[data-research="measured-recovery"] .research-metrics strong').first).to_be_visible()
        contrast=page.evaluate('''() => {
          const linear=v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4};
          return [...document.querySelectorAll('.overview [data-research] .research-metrics strong, .overview [data-research] .research-metrics p, .overview [data-research] .research-limit')].map(e=>{
            const c=getComputedStyle(e).color.match(/[0-9.]+/g).slice(0,3).map(Number);
            const l=.2126*linear(c[0])+.7152*linear(c[1])+.0722*linear(c[2]);return 1.05/(l+.05);
          });
        }''')
        assert contrast and min(contrast)>=4.5,contrast
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        page.screenshot(path=str(out/'overview-contrast-mobile.png'),full_page=True)
        assert not errors,errors
        browser.close()
    summary={'passed':True,'native_import_retained':True,'phase_status':result['diagnosis']['category'],
        'recovery_status':recovery['status'],'experiment_id':recovery['experiment_id'],
        'export_verified':True,'mobile_widths':mobile,'minimum_tested_white_surface_text_contrast':min(contrast),'page_errors':errors}
    (out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))


if __name__=='__main__':main()
