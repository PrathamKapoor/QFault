"""Browser acceptance for the landing hero and the landing -> workbench transition; real server, no fake science.

The hero is the transplanted MENTAL.AI entry composition (D-038): letters assemble, the WebGL sculpture appears
after 2 s, Enter Workbench runs the entry handover and then the preserved PixelSwap transition.
"""
import argparse, json, os, time
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

BASE = os.environ.get('QFAULT_BASE_URL', 'http://127.0.0.1:8000')
WORKBENCH = 'Quantum investigation intelligence.'


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--out', required=True); args = parser.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=False)
    errors, observations = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = context.new_page(); page.on('pageerror', lambda e: errors.append(str(e)))
        # Frozen browser time captures genuine short-lived entrance states; content is never mocked.
        page.clock.install(time=0); page.clock.pause_at(1000)
        page.goto(BASE + '/', wait_until='networkidle')
        page.clock.run_for(100)
        expect(page.get_by_role('heading', name='QFAULT', exact=True)).to_be_attached()
        expect(page.locator('.entry.entry--live')).to_be_attached(timeout=10000)
        expect(page.locator('.entry__stage canvas[data-engine="webgl"]')).to_be_attached(timeout=15000)
        assert page.locator('.entry.entry--hero-live').count() == 0  # sculpture held back during letter assembly
        page.clock.run_for(600); page.screenshot(path=str(out / 'entrance-letters.png'))
        page.clock.run_for(1500)
        expect(page.locator('.entry.entry--hero-live')).to_be_attached()
        page.clock.run_for(2500); page.screenshot(path=str(out / 'hero.png'))
        page.clock.resume()
        page.clock.pause_at(page.evaluate('Date.now()') + 50)
        page.get_by_role('button', name='Enter Workbench', exact=True).first.click()
        page.clock.run_for(350)
        expect(page.locator('[data-phase="reframe"]')).to_be_attached()
        expect(page.locator('.entry.entry--split')).to_be_attached()
        expect(page.get_by_text('Your quantum laboratory is ready.')).to_be_visible()
        page.screenshot(path=str(out / 'handover.png'), animations='disabled')
        page.clock.run_for(720)
        expect(page.locator('.pixel-swap[data-transitioning="true"]')).to_be_attached(); page.screenshot(path=str(out / 'pixel-swap.png'))
        page.clock.resume()
        expect(page.get_by_role('heading', name=WORKBENCH)).to_be_focused()
        expect(page.locator('.overview[data-ready="true"]')).to_be_attached(timeout=30000)
        assert page.locator('.entry__stage canvas').count() == 0  # hero GL context released after entry
        page.screenshot(path=str(out / 'workbench.png'), full_page=True)
        page.get_by_role('button', name='New Investigation', exact=True).first.click()
        expect(page.get_by_label('Circuit family')).to_be_visible()
        page.go_back(); expect(page.get_by_role('heading', name=WORKBENCH)).to_be_visible()
        page.go_forward(); expect(page.get_by_label('Circuit family')).to_be_visible()
        page.reload(); expect(page.get_by_label('Circuit family')).to_be_visible()
        for w, h in [(1920, 1080), (1440, 900), (1366, 768), (768, 1024), (390, 844), (375, 812), (360, 800)]:
            page.set_viewport_size({'width': w, 'height': h}); page.goto(BASE + '/')
            expect(page.locator('[data-phase="hero"]')).to_be_attached()
            expect(page.locator('.entry__stage canvas[data-engine="webgl"]')).to_be_attached(timeout=15000)
            page.wait_for_timeout(1000)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), w
            page.screenshot(path=str(out / f'landing-{w}.png'))
            page.goto(BASE + '/#/workbench'); expect(page.get_by_role('heading', name=WORKBENCH)).to_be_visible(timeout=30000)
            expect(page.locator('.overview[data-ready="true"]')).to_be_attached(timeout=30000)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), w
            page.screenshot(path=str(out / f'workbench-{w}.png'), full_page=True)
        reduced = browser.new_context(reduced_motion='reduce', viewport={'width': 1440, 'height': 900}); r = reduced.new_page()
        r.on('pageerror', lambda e: errors.append(str(e))); r.goto(BASE + '/')
        expect(r.locator('[data-phase="hero"]')).to_be_attached()
        expect(r.locator('.entry.entry--hero-live')).to_be_attached(timeout=5000)  # no 2 s hold under reduced motion
        expect(r.locator('.entry__stage canvas[data-engine="webgl"]')).to_be_attached(timeout=15000)
        r.wait_for_timeout(800); r.screenshot(path=str(out / 'reduced-hero.png'))
        r.get_by_role('button', name='Enter Workbench', exact=True).first.click()
        expect(r.get_by_role('heading', name=WORKBENCH)).to_be_focused()
        fallback = browser.new_context(reduced_motion='reduce')
        fallback.add_init_script("const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(type,...args){return /webgl/.test(type)?null:original.call(this,type,...args)}")
        f = fallback.new_page(); f.on('pageerror', lambda e: errors.append(str(e))); f.goto(BASE + '/')
        expect(f.locator('.entry__stage canvas[data-engine="fallback-2d"]')).to_be_attached(timeout=15000)
        expect(f.get_by_role('button', name='Enter Workbench', exact=True).first).to_be_visible()
        f.wait_for_timeout(800); f.screenshot(path=str(out / 'webgl-fallback.png'))
        f.get_by_role('button', name='Enter Workbench', exact=True).first.click()
        expect(f.get_by_role('heading', name=WORKBENCH)).to_be_focused()
        context.close(); reduced.close(); fallback.close()
        perf = browser.new_context(); timed = perf.new_page(); start = time.perf_counter()
        timed.goto(BASE + '/', wait_until='domcontentloaded')
        expect(timed.locator('.entry__stage canvas[data-engine="webgl"]')).to_be_attached(timeout=15000)
        observations.append({'fresh_context_webgl_seconds': round(time.perf_counter() - start, 3),
                             'navigation': timed.evaluate('performance.getEntriesByType("navigation")[0].toJSON()')})
        assert not errors, errors
        browser.close()
    (out / 'summary.json').write_text(json.dumps({'page_errors': errors, 'observations': observations, 'responsive_sizes': 7,
                                                  'reduced_motion': True, 'webgl_fallback': True, 'navigation': True}, indent=2))


if __name__ == '__main__':
    main()
