import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch()
    pg=await b.new_page(viewport={"width":440,"height":956},device_scale_factor=3,locale="en-US")
    await pg.add_init_script("window.Capacitor={getPlatform:()=>'ios',isNativePlatform:()=>false}")
    await pg.goto("file:///home/claude/fatcat-todo/www/index.html");await pg.wait_for_timeout(600)
    await pg.get_by_text("Skip").click();await pg.wait_for_timeout(400)
    await pg.evaluate("""S.settings.lang='en';U.products={fatcat_pro_monthly:{price:'$1.99',micros:1990000},fatcat_pro_yearly:{price:'$14.99',micros:14990000},fatcat_pro_lifetime:{price:'$19.99',micros:19990000}};U.view='premium';render()""")
    await pg.wait_for_timeout(500)
    print(await pg.evaluate("document.body.innerText.match(/\\$[0-9.]+/g)"))
    print(await pg.evaluate("(document.body.innerText.match(/Apple ID[^\\n]*/)||['no apple'])[0].slice(0,80)"))
    await pg.screenshot(path="/home/claude/fatcat-todo/store/ios/iap-review.png")
    await b.close()
asyncio.run(main())
