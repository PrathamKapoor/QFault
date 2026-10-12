"""Browser acceptance for the cinematic shell; real server, no fake science."""
import argparse,json,time
from pathlib import Path
from playwright.sync_api import sync_playwright,expect

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
    errors=[];observations=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        context=browser.new_context(viewport={'width':1440,'height':900})
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        # Freeze browser time for genuine captures of short-lived states. This
        # controls timers, not pixels/content; no scientific response is mocked.
        page.clock.install(time=0);page.clock.pause_at(1000)
        page.goto('http://127.0.0.1:8000/',wait_until='networkidle')
        page.clock.run_for(50)
        expect(page.get_by_role('heading',name='QFAULT',exact=True)).to_be_attached()
        for phase,advance in [('hyperspeed',350),('techtext',150),('hero',350)]:
            page.clock.run_for(advance)
            expect(page.locator(f'[data-phase="{phase}"]')).to_be_attached(timeout=10000)
            if phase=='hyperspeed':
                expect(page.locator('.intro-speed canvas')).to_be_attached(timeout=15000)
                page.clock.run_for(150)
                expect(page.locator('.intro-speed canvas[data-rendered="true"]')).to_be_attached()
            elif phase=='techtext':
                expect(page.locator('.tech-reveal canvas')).to_be_attached()
                page.clock.run_for(300)
            else:
                page.clock.run_for(350)
                expect(page.locator('.sculpture canvas[data-engine="webgl"]')).to_be_attached(timeout=15000)
                page.clock.run_for(1000)
                expect(page.locator('.sculpture canvas[data-rendered="true"]')).to_be_attached()
            page.screenshot(path=str(out/(phase+'.png')))
        page.clock.resume()
        expect(page.locator('.sculpture canvas[data-engine="webgl"]')).to_be_attached()
        page.wait_for_timeout(500);page.screenshot(path=str(out/'landing-highlight.png'))
        page.clock.pause_at(page.evaluate('Date.now()')+50)
        page.get_by_role('button',name='Enter Workbench',exact=True).click()
        page.clock.run_for(350)
        expect(page.locator('[data-phase="reframe"]')).to_be_attached();page.screenshot(path=str(out/'reframe.png'),animations='disabled')
        page.clock.run_for(420)
        page.clock.run_for(100)
        page.clock.run_for(200)
        expect(page.locator('.pixel-swap[data-transitioning="true"]')).to_be_attached();page.screenshot(path=str(out/'pixel-swap.png'))
        page.clock.resume()
        expect(page.get_by_role('heading',name='Quantum investigation intelligence.')).to_be_focused()
        expect(page.locator('.overview[data-ready="true"]')).to_be_attached()
        assert page.locator('.sculpture canvas').count()==0
        page.screenshot(path=str(out/'workbench.png'),full_page=True)
        page.get_by_role('button',name='New Investigation',exact=True).first.click()
        expect(page.get_by_label('Circuit family')).to_be_visible()
        page.go_back();expect(page.get_by_role('heading',name='Quantum investigation intelligence.')).to_be_visible()
        page.go_forward();expect(page.get_by_label('Circuit family')).to_be_visible()
        page.reload();expect(page.get_by_label('Circuit family')).to_be_visible()
        for w,h in [(1920,1080),(1440,900),(1366,768),(768,1024),(390,844)]:
            page.set_viewport_size({'width':w,'height':h});page.goto('http://127.0.0.1:8000/')
            expect(page.locator('[data-phase="hero"]')).to_be_attached()
            expect(page.locator('.sculpture canvas[data-rendered="true"]')).to_be_attached(timeout=15000)
            page.wait_for_timeout(1000)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            page.screenshot(path=str(out/f'landing-{w}.png'))
            page.goto('http://127.0.0.1:8000/#/workbench');expect(page.get_by_role('heading',name='Quantum investigation intelligence.')).to_be_visible()
            expect(page.locator('.overview[data-ready="true"]')).to_be_attached()
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            page.screenshot(path=str(out/f'workbench-{w}.png'),full_page=True)
        reduced=browser.new_context(reduced_motion='reduce',viewport={'width':1440,'height':900});r=reduced.new_page();r.goto('http://127.0.0.1:8000/')
        expect(r.locator('[data-phase="hero"]')).to_be_attached()
        expect(r.locator('.sculpture canvas[data-rendered="true"]')).to_be_attached(timeout=15000)
        expect(r.locator('.metal-atmosphere canvas[data-rendered="true"]')).to_be_attached(timeout=15000)
        r.screenshot(path=str(out/'reduced-hero.png'))
        r.get_by_role('button',name='Enter Workbench',exact=True).click()
        expect(r.get_by_role('heading',name='Quantum investigation intelligence.')).to_be_focused()
        fallback=browser.new_context(reduced_motion='reduce')
        fallback.add_init_script("const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(type,...args){return /webgl/.test(type)?null:original.call(this,type,...args)}")
        f=fallback.new_page();f.goto('http://127.0.0.1:8000/');expect(f.locator('.sculpture-fallback')).to_be_visible()
        f.screenshot(path=str(out/'webgl-fallback.png'));f.get_by_role('button',name='Enter Workbench',exact=True).click()
        expect(f.get_by_role('heading',name='Quantum investigation intelligence.')).to_be_focused()
        # Separate unscreenshoted measurement; graphics captures can stall software GL.
        context.close();reduced.close();fallback.close()
        perf=browser.new_context();timed=perf.new_page();start=time.perf_counter()
        timed.goto('http://127.0.0.1:8000/',wait_until='domcontentloaded')
        expect(timed.locator('[data-phase="hero"]')).to_be_attached(timeout=15000)
        observations.append({'fresh_context_hero_seconds':round(time.perf_counter()-start,3),
            'navigation':timed.evaluate('performance.getEntriesByType("navigation")[0].toJSON()')})
        assert not errors,errors
        browser.close()
    (out/'summary.json').write_text(json.dumps({'page_errors':errors,'observations':observations,'responsive_sizes':5,'reduced_motion':True,'webgl_fallback':True,'navigation':True},indent=2))

if __name__=='__main__':main()
