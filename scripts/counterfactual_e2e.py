"""Real editor -> measured intervention -> export; desktop and mobile inspection."""
import json
import os
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from qfault.storage import verify_export
from scripts.lab_e2e import paste

BASE=os.environ.get('QFAULT_BASE_URL','http://127.0.0.1:8000')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/recovery-browser');args=parser.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
    c={'schema_version':1,'name':'Measured bit inversion','n_qubits':2,
       'input':{'kind':'computational_basis','bitstring':'00'},'gates':[{'name':'x','qubits':[0]}]}
    target={'kind':'target_state','amplitudes':[[1.,0.],[0.,0.],[0.,0.],[0.,0.]],'fidelity_tolerance':.2}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        ctx=browser.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce')
        page=ctx.new_page(); errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        console=[];page.on('console',lambda m:console.append(m.text) if m.type=='error' else None)
        page.goto(BASE+'/#/lab')
        page.get_by_label('Contract type').select_option('target_state')
        paste(page,'Circuit JSON',c);paste(page,'Contract JSON',target)
        page.get_by_role('button',name='Measured recovery').click()
        expect(page.get_by_role('heading',name='Counterfactual recovery',exact=True)).to_be_visible()
        with page.expect_response(lambda r:r.url.endswith('/api/lab/recoveries') and r.request.method=='POST',timeout=120000) as response:
            page.get_by_role('button',name='Run measured recovery').click()
        assert response.value.status==201,response.value.text()
        result=response.value.json();eid=result['experiment_id']
        assert result['status']=='VERIFIED_UNDER_DECLARED_CONTRACT'
        expect(page.get_by_text('verified under declared contract').first).to_be_visible()
        expect(page.get_by_text('Reduction in normalized worst-claim discrepancy',exact=False)).to_be_visible()
        expect(page.get_by_text('Dimensionless contract-tolerance units',exact=False)).to_be_visible()
        verification=result['verification']
        delta=verification['original']['loss_interval'][0]-verification['candidate']['loss_interval'][1]
        assert abs(delta-verification['improvement_lower'])<1e-12
        page.screenshot(path=str(out/'measured-recovery-desktop.png'),full_page=True)
        page.get_by_role('heading',name='Candidate comparison',exact=True).scroll_into_view_if_needed()
        page.screenshot(path=str(out/'candidate-comparison.png'))
        page.locator('.recovery-diff').screenshot(path=str(out/'circuit-diff.png'))
        page.get_by_role('heading',name='Independent fresh verification',exact=True).scroll_into_view_if_needed()
        page.screenshot(path=str(out/'fresh-verification.png'))
        with page.expect_download() as download:page.get_by_role('link',name='Export recovery evidence').click()
        downloaded=json.loads(Path(download.value.path()).read_bytes());assert verify_export(downloaded)['valid']
        page.reload();expect(page.get_by_text('Artifact hashes verified.').first).to_be_visible()
        # History dispatch must recognize the new record kind.
        page.goto(BASE+'/#/experiments/'+eid);expect(page).to_have_url(BASE+'/#/lab/recovery/'+eid)
        for width,height in ((390,844),(375,812),(360,800)):
            page.set_viewport_size({'width':width,'height':height});page.goto(BASE+'/#/lab/recovery/'+eid)
            expect(page.get_by_role('heading',name='Counterfactual recovery',exact=True)).to_be_visible()
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            page.screenshot(path=str(out/f'mobile-{width}.png'),full_page=True)
        clean={**c,'gates':[]}
        r=ctx.request.post(BASE+'/api/lab/recoveries',data={'circuit':clean,'contract':target,'environment':{'readout':.35}}).json()
        assert r['status']=='NOISE_CONTROL_ABSTENTION'
        page.set_viewport_size({'width':1440,'height':900});page.goto(BASE+'/#/lab/recovery/'+r['experiment_id'])
        expect(page.get_by_text('noise control abstention').first).to_be_visible()
        page.screenshot(path=str(out/'noise-negative-control.png'),full_page=True)
        page.goto(BASE+'/#/workbench');expect(page.get_by_role('heading',name='Quantum investigation intelligence.')).to_be_visible()
        page.screenshot(path=str(out/'preserved-workbench.png'),full_page=True)
        assert not errors and not console,(errors,console)
        (out/'summary.json').write_text(json.dumps({'experiment_id':eid,'negative_id':r['experiment_id'],'page_errors':errors,
             'export_verified':True,'console_errors':console,'real_aer':result['executions'][0]['backend_name'],'mobile_widths':[390,375,360]},indent=2))
        browser.close()


if __name__=='__main__':main()
