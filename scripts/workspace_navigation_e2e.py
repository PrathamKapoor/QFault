"""Regression checks for route identity, drafts and visible API failures."""
import argparse,asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright,expect

async def check(out):
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True)
        context=await browser.new_context(reduced_motion='reduce',viewport={'width':1440,'height':900})
        page=await context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        await page.goto((__import__('os').environ.get('QFAULT_BASE_URL','http://127.0.0.1:8000') + '/#/investigation'))
        await page.get_by_label('Circuit family').select_option('ghz')
        await page.get_by_label('Qubit count').select_option('4')
        await page.get_by_label('Shots per execution').fill('1024')
        await page.get_by_role('link',name='QFAULT home').click()
        await page.get_by_role('button',name='Open workbench',exact=True).click()
        await page.get_by_role('link',name='New Investigation',exact=True).click()
        await expect(page.get_by_label('Circuit family')).to_have_value('ghz')
        await expect(page.get_by_label('Qubit count')).to_have_value('4')
        await expect(page.get_by_label('Shots per execution')).to_have_value('1024')
        # This test asserts the legacy template tab identity. History now also contains
        # custom/recovery records with different views: create its own explicit fixtures.
        ids=[]
        for seed in (419,421):
            response=await context.request.post((__import__('os').environ.get('QFAULT_BASE_URL','http://127.0.0.1:8000') + '/api/experiments'),
                data={'family':'bell','scenario':'clean','backend':'aer','seed':seed})
            assert response.status==201
            ids.append((await response.json())['experiment_id'])
        a,b=ids
        async def delay(route):
            response=await route.fetch();await asyncio.sleep(.7);await route.fulfill(response=response)
        await page.route('**/api/experiments/'+a,delay)
        await page.goto((__import__('os').environ.get('QFAULT_BASE_URL','http://127.0.0.1:8000') + '/#/experiments/')+a,wait_until='domcontentloaded')
        await page.wait_for_timeout(100)
        await page.goto((__import__('os').environ.get('QFAULT_BASE_URL','http://127.0.0.1:8000') + '/#/experiments/')+b,wait_until='domcontentloaded')
        await expect(page.locator('.tabs>span')).to_have_text(b[-12:])
        await page.wait_for_timeout(900)
        await expect(page.locator('.tabs>span')).to_have_text(b[-12:])
        await page.reload();await expect(page.locator('.tabs>span')).to_have_text(b[-12:])
        await page.goto((__import__('os').environ.get('QFAULT_BASE_URL','http://127.0.0.1:8000') + '/#/experiments/experiment_00000000000000000000000000000000'))
        await expect(page.get_by_role('alert')).to_contain_text('not found')
        assert await page.get_by_role('link',name='Export investigation JSON').count()==0
        failed=await browser.new_context(reduced_motion='reduce');f=await failed.new_page()
        await f.route('**/api/circuits',lambda route:route.abort('failed'))
        await f.goto((__import__('os').environ.get('QFAULT_BASE_URL','http://127.0.0.1:8000') + '/#/workbench'))
        await expect(f.get_by_role('alert')).to_be_visible()
        await f.get_by_role('link',name='Saved investigations').click()
        await expect(f.get_by_role('alert')).to_be_visible()
        await page.set_viewport_size({'width':390,'height':844})
        await page.get_by_role('button',name='Toggle navigation').click()
        await expect(page.get_by_role('link',name='Saved investigations')).to_be_visible()
        await page.keyboard.press('Escape')
        await expect(page.get_by_role('button',name='Toggle navigation')).to_be_focused()
        assert not errors,errors
        await browser.close()
    out.write_text(json.dumps({'draft_preserved':True,'real_response_route_race':True,'saved_route_refresh':True,'missing_record_clears_selection':True,'overview_history_api_failure':True,'mobile_navigation_escape':True,'page_errors':errors},indent=2))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():raise FileExistsError(out)
    asyncio.run(check(out))

if __name__=='__main__':main()
