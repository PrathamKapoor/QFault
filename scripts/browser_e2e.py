"""Actual local browser scientific journey; no mocked successful responses."""
import argparse,json
from pathlib import Path
from importlib.metadata import version
from playwright.sync_api import sync_playwright,expect
from qfault.storage import verify_export

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--record-video',action='store_true');args=parser.parse_args()
    root=Path(args.out);root.mkdir(parents=True,exist_ok=False)
    console_errors=[];page_errors=[];failed_requests=[];http_errors=[];rows=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        recording={'record_video_dir':str(root/'video'),'record_video_size':{'width':1440,'height':900}} if args.record_video else {}
        context=browser.new_context(viewport={'width':1600,'height':1000},accept_downloads=True,**recording);page=context.new_page()
        page.on('console',lambda msg:console_errors.append(msg.text) if msg.type=='error' else None)
        page.on('pageerror',lambda err:page_errors.append(str(err)))
        page.on('requestfailed',lambda req:failed_requests.append({'url':req.url,'failure':req.failure}))
        page.on('response',lambda response:http_errors.append({'url':response.url,'status':response.status}) if response.status>=400 else None)
        page.goto('http://127.0.0.1:8000/#/investigation',wait_until='networkidle')
        expect(page.get_by_role('heading',name='Investigate. Recover. Verify.')).to_be_visible()
        expect(page.get_by_role('heading',name='Coherent Bell state')).to_be_visible()
        assert page.get_by_label('Diagnostic policy').input_value()=='fixed'
        expect(page.get_by_label('Diagnostic policy').locator('option[value=phase]')).to_have_text('Phase-sensitive evidence · higher cost')
        page.get_by_label('Circuit family').select_option('qft');expect(page.get_by_role('heading',name='Fourier output for basis input |001⟩')).to_be_visible()
        page.get_by_label('Qubit count').select_option('4');expect(page.get_by_role('heading',name='Fourier output for basis input |0001⟩')).to_be_visible()
        page.get_by_label('Circuit family').select_option('bell')
        page.get_by_label('Diagnostic policy').select_option('phase');page.get_by_label('Simulation backend').select_option('aer')
        def investigate(scenario,expected_category,shots=2048):
            page.get_by_label('Execution scenario').select_option(scenario);page.get_by_label('Shots per execution').fill(str(shots))
            with page.expect_response(lambda r:r.url.endswith('/api/experiments') and r.request.method=='POST') as response:
                page.get_by_role('button',name='Run investigation').click()
                loading=page.get_by_role('button',name='Executing Qiskit').is_disabled() if page.get_by_role('button',name='Executing Qiskit').count() else False
            r=response.value;assert r.status==201;data=r.json();assert data['diagnosis']['category']==expected_category
            expect(page).to_have_url('http://127.0.0.1:8000/#/experiments/'+data['experiment_id'])
            expect(page.get_by_role('heading',name={'NO_SIGNIFICANT_FAILURE_DETECTED':'No significant failure detected','LOGICAL_CIRCUIT_DEFECT':'Logical circuit defect','NOISE_CONSISTENT_DEGRADATION':'Noise-consistent degradation','INSUFFICIENT_EVIDENCE':'Insufficient evidence'}[expected_category],exact=True)).to_be_visible()
            expect(page.get_by_role('heading',name='Expected vs. observed',exact=True)).to_be_visible()
            assert sum(e['executed_shots'] for e in data['executions'])==data['cost']['shots']
            assert all(e['backend_name']=='qiskit_aer.AerSimulator/density_matrix' for e in data['executions'])
            assert data['candidate']['n_qubits']==int(page.get_by_label('Qubit count').input_value())
            row={'family':data['configuration']['family'],'n_qubits':data['candidate']['n_qubits'],'scenario':scenario,'shots_per_execution':shots,'experiment_id':data['experiment_id'],'diagnosis':expected_category,'actual_shots':data['cost']['shots'],'evaluations':data['cost']['evaluations'],'loading_observed':loading,'recovery':(data['recovery'] or {}).get('status')};rows.append(row)
            # Completion includes the real history refresh and verification
            # requests, not just the experiment POST response.
            expect(page.get_by_role('button',name='Run investigation')).to_be_enabled(timeout=30000)
            expect(page.get_by_text('Artifact hashes verified',exact=True)).to_be_visible()
            (root/(data['experiment_id']+'.json')).write_text(json.dumps(data,indent=2),encoding='utf8')
            if args.record_video: page.wait_for_timeout(2000)  # Genuine reading hold in silent raw footage.
            return data
        for family in ['qft','ghz']:
            page.get_by_label('Circuit family').select_option(family);page.get_by_label('Qubit count').select_option('4')
            configured=investigate('clean','NO_SIGNIFICANT_FAILURE_DETECTED');assert configured['contract']['n_qubits']==4
        page.get_by_label('Circuit family').select_option('bell')
        healthy=investigate('clean','NO_SIGNIFICANT_FAILURE_DETECTED')
        bad=investigate('remove','LOGICAL_CIRCUIT_DEFECT')
        expect(page.get_by_role('heading',name='Competing explanations')).to_be_visible()
        expect(page.get_by_role('cell',name='Privileged simulator calculation',exact=True)).to_be_visible()
        page.get_by_text('Inspect Qiskit circuit text',exact=True).click()
        expect(page.locator('.circuit-diagram')).to_contain_text('q_0:')
        expect(page.get_by_role('heading',name='Phase-sensitive measurements')).to_be_visible()
        assert page.locator('.distribution').first.locator('text.axis').all_text_contents()[5:9]==['00','01','10','11']
        page.screenshot(path=str(root/'evidence-desktop.png'),full_page=True)
        page.get_by_role('tab',name='Recovery',exact=True).click()
        assert bad['recovery']['status']=='VERIFIED'
        expect(page.locator('.recovery .badge')).to_have_text('VERIFIED')
        expect(page.get_by_text('Fresh candidate phase-basis quality',exact=True)).to_be_visible()
        expect(page.get_by_text(str(bad['recovery']['verification']['validation_seed']),exact=True)).to_be_visible()
        page.screenshot(path=str(root/'recovery-desktop.png'),full_page=True)
        if args.record_video: page.wait_for_timeout(3000)
        page.get_by_role('tab',name='Report',exact=True).click()
        with page.expect_download() as download_info:page.get_by_role('link',name='Export investigation JSON').click()
        download=download_info.value;download.save_as(root/'investigation-export.json');report=json.loads((root/'investigation-export.json').read_bytes());assert verify_export(report)['valid'];assert report['investigation']['experiment_id']==bad['experiment_id']
        page.reload(wait_until='networkidle');expect(page.get_by_role('heading',name='Logical circuit defect',exact=True)).to_be_visible()
        expect(page.locator('.tabs>span')).to_have_text(bad['experiment_id'][-12:])
        page.locator('.history button').filter(has_text=bad['experiment_id'][-10:]).click();expect(page.get_by_role('heading',name='Logical circuit defect',exact=True)).to_be_visible()
        expect(page.get_by_label('Diagnostic policy')).to_have_value('phase')
        expect(page.get_by_label('Simulation backend')).to_have_value('aer')
        expect(page.get_by_label('Execution scenario')).to_have_value('remove')
        page.get_by_role('button',name='Recheck integrity').click();expect(page.get_by_text('Artifact hashes verified',exact=True)).to_be_visible()
        page.get_by_label('Diagnostic policy').select_option('phase');page.get_by_label('Simulation backend').select_option('aer')
        noise=investigate('readout','NOISE_CONSISTENT_DEGRADATION');assert noise['recovery'] is None
        phase_fault=investigate('phase','LOGICAL_CIRCUIT_DEFECT');assert phase_fault['recovery']['status']=='VERIFIED'
        low=investigate('phase','INSUFFICIENT_EVIDENCE',64);assert low['recovery'] is None
        page.get_by_role('tab',name='Benchmark',exact=True).click();expect(page.get_by_role('heading',name='Separate frozen final comparison')).to_be_visible();expect(page.get_by_role('cell',name='66/68',exact=True)).to_be_visible()
        if args.record_video: page.wait_for_timeout(4000)
        page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(root/'mobile.png'),full_page=True)
        geometry=page.evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth})');assert geometry['scroll']<=geometry['width']+1,geometry
        # Actual invalid API request from a valid HTML input: 7000*2 exceeds fixed12000 budget.
        positive_console=list(console_errors);positive_http=list(http_errors)
        page.get_by_label('Shots per execution').fill('7000')
        with page.expect_response(lambda r:r.url.endswith('/api/experiments') and r.request.method=='POST') as invalid:page.get_by_role('button',name='Run investigation').click()
        assert invalid.value.status==422;expect(page.get_by_role('alert')).to_contain_text('budget must fund baseline and observation')
        page.screenshot(path=str(root/'invalid-input.png'),full_page=True)
        assert not page_errors and not failed_requests and not positive_console and not positive_http,{'page':page_errors,'requests':failed_requests,'console':positive_console,'http':positive_http}
        assert len(http_errors)==1 and http_errors[0]['status']==422
        summary={'artifact_directory':str(root),'bitstrings_sorted':True,'saved_configuration_restored':True,'qubit_configuration_verified':True,'expected_console_after_invalid':console_errors[len(positive_console):],'playwright':version('playwright'),'browser_version':browser.version,'browser_executable':p.chromium.executable_path,'mocked_scientific_successes':False,'workflows':rows,'contract_selection':True,'circuit_rendered':True,'independent_recovery_display':True,'download_export_verified':True,'refresh_and_history_reload':True,'integrity_recheck':True,'frozen_comparison_display':True,'mobile_geometry':geometry,'positive_console_errors':positive_console,'page_errors':page_errors,'failed_requests':failed_requests,'expected_invalid_http':http_errors,'invalid_error_display':True,'screenshots':['evidence-desktop.png','recovery-desktop.png','mobile.png','invalid-input.png'],'limitations':['Local installed Playwright/Chromium bridge; not fresh dependency installation','Single tested desktop/mobile sizes, not exhaustive device/browser coverage','Review remains pending; no automated test poses as human approval']}
        context.close()
        if args.record_video:
            video=Path(page.video.path());named=video.with_name('browser-workflow.webm');video.rename(named)
            summary['recording']={'path':str(named),'bytes':named.stat().st_size,'kind':'Genuine silent unedited browser capture; not a narrated final submission video'}
        browser.close()
        (root/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
