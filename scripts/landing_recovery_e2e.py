"""Real landing layout and interaction checks for the transplanted hero; no quantum responses mocked."""
import argparse, json, os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

BASE = os.environ.get('QFAULT_BASE_URL', 'http://127.0.0.1:8000')


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--out', required=True); args = parser.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=False)
    errors, console = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 900})
        context.add_init_script("sessionStorage.setItem('qfault-intro','1')")
        page = context.new_page(); page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('console', lambda m: console.append(m.text) if m.type == 'error' else None)
        page.goto(BASE + '/', wait_until='networkidle')
        expect(page.locator('.entry.entry--hero-live .entry__stage canvas[data-engine="webgl"]')).to_be_attached(timeout=20000)
        page.wait_for_timeout(1500)
        page.screenshot(path=str(out / 'hero-1440.png'))
        # One depth stage: back word plane, sculpture, front word plane, in that DOM/stacking order.
        order = page.evaluate("""() => [...document.querySelector('.entry__depth').children].map(e => e.className)""")
        assert order[0].startswith('entry__word-plane entry__word-plane--back') and order[1] == 'entry__stage' \
            and order[2].startswith('entry__word-plane entry__word-plane--front'), order
        word = page.locator('.entry__word-plane--front .entry__word').bounding_box()
        stage = page.locator('.entry__stage').bounding_box()
        assert word['width'] > 0.85 * stage['width'] and word['y'] > stage['y'] and word['y'] + word['height'] < stage['y'] + stage['height']
        expect(page.get_by_role('heading', name='How QFAULT works')).to_be_attached()
        for w, h in [(1920, 1080), (1440, 900), (1366, 768), (768, 1024), (390, 844), (375, 812), (360, 800)]:
            page.set_viewport_size({'width': w, 'height': h}); page.goto(BASE + '/')
            expect(page.locator('.entry__stage canvas[data-engine="webgl"]')).to_be_attached(timeout=20000)
            page.wait_for_timeout(1200)
            for selector in ['.landing-nav', '.entry__word-plane--front .entry__word', '.entry__headline', '.entry__copy .entry__sub',
                             '.entry__ctas .cta--primary', '.entry__ctas .cta--ghost']:
                rect = page.locator(selector).bounding_box()
                assert rect and rect['x'] >= 0 and rect['y'] >= 0 and rect['x'] + rect['width'] <= w + 1 and rect['y'] + rect['height'] <= h + 1, (w, selector, rect)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), w
            button = page.locator('.entry__ctas .cta--primary')
            assert button.evaluate('(e)=>{const r=e.getBoundingClientRect();return e.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2))}'), w
            page.screenshot(path=str(out / f'hero-{w}.png'))
        page.set_viewport_size({'width': 1440, 'height': 900}); page.goto(BASE + '/')
        expect(page.locator('.entry__stage canvas[data-engine="webgl"]')).to_be_attached(timeout=20000)
        page.wait_for_timeout(1500)
        detail = page.add_style_tag(content='.entry__word-plane,.entry__copy,.landing-nav,.entry__labels{visibility:hidden!important}')
        page.wait_for_timeout(200); page.locator('.entry__stage').screenshot(path=str(out / 'sculpture-closeup.png'))
        detail.evaluate('(e)=>e.remove()')
        page.get_by_role('link', name='Platform', exact=True).click()
        expect(page.locator('#platform')).to_be_in_viewport()
        assert page.evaluate('location.hash') in ('', '#/')
        page.evaluate('window.scrollTo(0,0)')
        page.locator('.entry__ctas .cta--ghost').click()
        expect(page.locator('#research')).to_be_in_viewport()
        assert page.evaluate('location.hash') in ('', '#/')
        page.get_by_role('button', name='Open the Quantum Workbench', exact=True).focus()
        page.clock.install()
        page.clock.pause_at(page.evaluate('Date.now()') + 50)
        page.keyboard.press('Enter')
        page.clock.run_for(350)
        expect(page.locator('[data-phase="reframe"]')).to_be_attached()
        page.screenshot(path=str(out / 'entry-transition.png'), animations='disabled')
        page.clock.resume()
        expect(page.get_by_role('heading', name='Quantum investigation intelligence.')).to_be_focused(timeout=20000)
        expect(page.locator('.overview[data-ready="true"]')).to_be_attached(timeout=30000)
        page.screenshot(path=str(out / 'workbench.png'), full_page=True)
        assert page.locator('.entry__stage canvas,.entry__grain canvas').count() == 0
        page.set_viewport_size({'width': 390, 'height': 844}); page.screenshot(path=str(out / 'workbench-mobile.png'), full_page=True)
        assert not errors and not console, (errors, console)
        (out / 'summary.json').write_text(json.dumps({'page_errors': errors, 'console_errors': console, 'viewports': 7,
                                                      'cta_hit_test': True, 'transition': True, 'layer_order': order}, indent=2))
        browser.close()


if __name__ == '__main__':
    main()
