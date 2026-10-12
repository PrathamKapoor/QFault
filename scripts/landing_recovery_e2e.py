"""Real landing visual review and interaction checks; no quantum responses mocked."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--baseline',action='store_true');args=parser.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
    errors=[];console=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        context=browser.new_context(viewport={'width':1440,'height':900})
        context.add_init_script("sessionStorage.setItem('qfault-intro','1')")
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('console',lambda m:console.append(m.text) if m.type=='error' else None)
        page.goto('http://127.0.0.1:8000/',wait_until='networkidle')
        expect(page.locator('.sculpture canvas[data-rendered="true"]')).to_be_attached(timeout=20000)
        page.wait_for_timeout(1200)
        page.screenshot(path=str(out/'hero-1440.png'))
        page.screenshot(path=str(out/'full-landing.png'),full_page=True)
        diagnostic=page.evaluate("""() => ({cores:navigator.hardwareConcurrency,canvases:[...document.querySelectorAll('canvas')].map(c=>({parent:c.parentElement.className,width:c.width,height:c.height,rect:c.getBoundingClientRect().toJSON()})),layers:['.landing','.hero-composition','.word-plane','.metal-atmosphere','.landing-vignette','.landing-copy'].map(s=>{const e=document.querySelector(s);if(!e)return {selector:s,missing:true};const c=getComputedStyle(e);return {selector:s,rect:e.getBoundingClientRect().toJSON(),opacity:c.opacity,z:c.zIndex,background:c.background,pointerEvents:c.pointerEvents}})})""")
        (out/'baseline-diagnostics.json').write_text(json.dumps(diagnostic,indent=2))
        style=page.add_style_tag(content='.hero-composition,.landing-copy,.landing-nav,.landing-foot{visibility:hidden!important}')
        page.wait_for_timeout(400);page.screenshot(path=str(out/'background-only.png'));style.evaluate('(e)=>e.remove()')
        if args.baseline:
            page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(1100);page.screenshot(path=str(out/'hero-390.png'))
            browser.close();return
        # The requested composition must share one depth stage, rather than
        # placing an isolated sculpture beside the name.
        expect(page.locator('.hero-composition .word-back')).to_have_count(1)
        expect(page.locator('.hero-composition .word-front')).to_have_count(1)
        assert page.locator('.hero-field-label,.sculpture-caption').count()==0
        expect(page.get_by_role('heading',name='How QFAULT works')).to_be_visible()
        for w,h in [(1920,1080),(1440,900),(1366,768),(768,1024),(390,844)]:
            page.set_viewport_size({'width':w,'height':h});page.goto('http://127.0.0.1:8000/')
            expect(page.locator('.sculpture canvas[data-rendered="true"]')).to_be_attached(timeout=20000)
            page.wait_for_timeout(1000)
            for selector in ['.landing-nav','.hero-brand.word-back','.landing-copy h2','.landing-description','.landing-actions .enter-button','.landing-actions .research-button']:
                rect=page.locator(selector).bounding_box();assert rect and rect['x']>=0 and rect['y']>=0 and rect['x']+rect['width']<=w+1 and rect['y']+rect['height']<=h+1,(w,selector,rect)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            button=page.locator('.landing-actions .enter-button');assert button.evaluate('(e)=>{const r=e.getBoundingClientRect();return e.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2))}')
            page.screenshot(path=str(out/f'hero-{w}.png'))
        page.set_viewport_size({'width':1440,'height':900});page.goto('http://127.0.0.1:8000/')
        expect(page.locator('.sculpture canvas[data-rendered="true"]')).to_be_attached(timeout=20000)
        page.wait_for_timeout(1000)
        detail=page.add_style_tag(content='.word-plane,.hero-eyebrow,.landing-nav,.landing-copy{visibility:hidden!important}')
        page.wait_for_timeout(200);page.locator('.sculpture').screenshot(path=str(out/'sculpture-closeup.png'))
        detail.evaluate('(e)=>e.remove()')
        page.get_by_role('link',name='Platform',exact=True).click()
        expect(page.locator('#platform')).to_be_in_viewport()
        assert page.evaluate('location.hash') in ('','#/')
        page.locator('.landing-actions .research-button').click()
        expect(page.locator('#research')).to_be_in_viewport()
        assert page.evaluate('location.hash') in ('','#/')
        page.get_by_role('button',name='Open the Quantum Workbench',exact=True).focus()
        # Observe the brief genuine state deterministically under software GL.
        page.clock.install()
        page.clock.pause_at(page.evaluate('Date.now()')+50)
        page.keyboard.press('Enter')
        page.clock.run_for(350)
        expect(page.locator('[data-phase="reframe"]')).to_be_attached()
        page.screenshot(path=str(out/'entry-transition.png'),animations='disabled')
        page.clock.resume()
        expect(page.get_by_role('heading',name='Quantum investigation intelligence.')).to_be_focused(timeout=20000)
        expect(page.locator('.overview[data-ready="true"]')).to_be_attached(timeout=30000)
        page.screenshot(path=str(out/'workbench.png'),full_page=True)
        assert page.locator('.sculpture canvas,.metal-atmosphere canvas').count()==0
        page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(out/'workbench-mobile.png'),full_page=True)
        assert not errors and not console,(errors,console)
        (out/'summary.json').write_text(json.dumps({'page_errors':errors,'console_errors':console,'viewports':5,'cta_hit_test':True,'transition':True},indent=2))
        browser.close()

if __name__=='__main__':main()
