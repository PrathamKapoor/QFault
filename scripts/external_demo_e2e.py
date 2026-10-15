"""Exercise the external QRNG circuit through the real laboratory editor."""
import argparse
import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

from qfault.storage import verify_export
from scripts.external_demo import example
from scripts.lab_e2e import paste


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='http://127.0.0.1:8000')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    ex = example()
    rows, errors, console, mobile = [], [], [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={'width': 1440, 'height': 900}, reduced_motion='reduce')
        page = ctx.new_page()
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('console', lambda m: console.append(m.text) if m.type == 'error' else None)
        for name, contract in [('z_only', ex['distribution']), ('complementary', ex['complementary'])]:
            page.goto(args.base + '/#/lab')
            page.get_by_label('Contract type').select_option(contract['kind'])
            paste(page, 'Circuit JSON', ex['candidate'])
            paste(page, 'Contract JSON', contract)
            page.get_by_label('Backend').select_option('aer')
            page.get_by_label('Diagnostic capability').select_option('measurement_only')
            page.get_by_label('Measurement policy').select_option('fixed')
            with page.expect_response(lambda r: r.url.endswith('/api/lab/investigations') and r.request.method == 'POST') as response:
                page.get_by_role('button', name='Run investigation').click()
            assert response.value.status == 201, response.value.text()
            inv = response.value.json()
            want = 'NO_SIGNIFICANT_DISCREPANCY' if name == 'z_only' else 'SIGNIFICANT_DISCREPANCY'
            assert inv['diagnosis']['category'] == want and not inv['privileged_operations']
            expect(page.get_by_role('heading', name='Claims and uncertainty')).to_be_visible()
            page.screenshot(path=str(args.out / (name + '.png')))
            rows.append({'stage': name, 'experiment_id': inv['experiment_id'], 'category': want, 'shots': inv['cost']['shots']})
        page.get_by_role('button', name='Measured recovery →', exact=True).click()
        with page.expect_response(lambda r: r.url.endswith('/api/lab/recoveries') and r.request.method == 'POST', timeout=180000) as response:
            page.get_by_role('button', name='Run measured recovery').click()
        assert response.value.status == 201, response.value.text()
        result = response.value.json()
        assert result['status'] == 'VERIFIED_UNDER_DECLARED_CONTRACT'
        assert result['localization']['causal_origin'] == 'NOT_IDENTIFIED'
        expect(page.get_by_role('heading', name='Candidate comparison')).to_be_visible()
        page.screenshot(path=str(args.out / 'external-recovery-desktop.png'))
        with page.expect_download() as download:
            page.get_by_role('link', name='Export recovery evidence').click()
        report = json.loads(Path(download.value.path()).read_bytes())
        assert verify_export(report)['valid']
        for width in (390, 375, 360):
            page.set_viewport_size({'width': width, 'height': 844})
            page.goto(args.base + '/#/lab/recovery/' + result['experiment_id'])
            expect(page.get_by_role('heading', name='Counterfactual recovery', exact=True)).to_be_visible()
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
            page.screenshot(path=str(args.out / f'external-mobile-{width}.png'))
            mobile.append({'width': width, 'overflow': False})
        assert not errors and not console, (errors, console)
        browser.close()
    (args.out / 'summary.json').write_text(json.dumps({'source_path': ex['source_path'], 'rows': rows,
        'recovery_id': result['experiment_id'], 'recovery_status': result['status'],
        'causal_origin': result['localization']['causal_origin'], 'export_verified': True,
        'mobile': mobile, 'page_errors': errors, 'console_errors': console}, indent=2))
    print('External circuit editor, complementary measurement, fresh recovery, export and three mobile widths passed')


if __name__ == '__main__': main()
