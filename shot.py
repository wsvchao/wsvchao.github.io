import sys, asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width":390,"height":844}, device_scale_factor=2)
        errs=[]
        pg.on("console", lambda m: errs.append(m.type+": "+m.text) if m.type in ("error","warning") else None)
        pg.on("pageerror", lambda e: errs.append("PAGEERROR: "+str(e)))
        await pg.goto("file:///home/claude/app/index.html")
        await pg.wait_for_timeout(1400)
        await pg.screenshot(path="/tmp/s1.png")
        # topic detail: 安息日
        await pg.click("text=安息日")
        await pg.wait_for_timeout(500)
        await pg.screenshot(path="/tmp/s2.png")
        # sequence drill
        await pg.click("[data-seq]")
        await pg.wait_for_timeout(400)
        await pg.click("[data-reveal]")
        await pg.wait_for_timeout(300)
        await pg.screenshot(path="/tmp/s3.png")
        # verse drill
        await pg.click("[data-back]"); await pg.wait_for_timeout(300)
        await pg.click(".entry"); await pg.wait_for_timeout(400)
        await pg.screenshot(path="/tmp/s4.png")
        await pg.click(".vrow"); await pg.wait_for_timeout(400)
        await pg.screenshot(path="/tmp/s5.png")
        # english + dark
        await pg.click("[data-lang='en']"); await pg.wait_for_timeout(300)
        await pg.screenshot(path="/tmp/s6.png")
        await pg.emulate_media(color_scheme="dark"); await pg.wait_for_timeout(300)
        await pg.click("[data-back]"); await pg.click("[data-back]"); await pg.wait_for_timeout(400)
        await pg.screenshot(path="/tmp/s7.png")
        print("CONSOLE:", errs[:12] if errs else "clean")
        await b.close()
asyncio.run(main())
