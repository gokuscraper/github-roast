
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def _launch():
    from cloakbrowser import launch_async
    from scraper.config import BASE_URL, PAGE_LOAD_TIMEOUT, VIEWPORT
    pw = await launch_async(headless=True)
    ctx = await pw.new_context(viewport=VIEWPORT)
    page = await ctx.new_page()
    page.set_default_timeout(PAGE_LOAD_TIMEOUT)
    for attempt in range(5):
        await page.goto(BASE_URL, wait_until="networkidle")
        t = await page.title() if hasattr(page, 'title') else ""
        if "Security" not in t:
            return pw, ctx, page
        await asyncio.sleep(2)
    raise RuntimeError(f"Vercel bypass failed: {t}")
    return pw, ctx, page

async def main():
    username = sys.argv[1]
    pw, ctx, page = await _launch()
    try:
        user_raw = await page.evaluate(
            f"fetch('/api/user/{username}').then(r=>r.json())"
        )
        tweets_raw = await page.evaluate(
            f"fetch('/api/tweets/{username}').then(r=>r.json())"
        )
        print(json.dumps({"user": user_raw, "tweets": tweets_raw}, ensure_ascii=False))
    finally:
        await ctx.close()
        await pw.stop()

asyncio.run(main())
