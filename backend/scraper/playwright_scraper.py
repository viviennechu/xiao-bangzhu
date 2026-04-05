"""Playwright fallback scraper for JavaScript-rendered pages."""
try:
    from playwright.async_api import async_playwright
    _PLAYWRIGHT_AVAILABLE = True
except ImportError:
    _PLAYWRIGHT_AVAILABLE = False


async def scrape_with_playwright(url: str) -> dict:
    """Use Playwright headless browser to scrape JS-rendered pages."""
    if not _PLAYWRIGHT_AVAILABLE:
        return {"name": "", "description": "", "price": "", "images": []}
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            )
            await page.goto(url, wait_until="networkidle", timeout=30000)

            # Name
            name = ""
            h1 = await page.query_selector("h1")
            if h1:
                name = (await h1.inner_text()).strip()

            # Description via meta or visible text
            description = await page.evaluate("""() => {
                const meta = document.querySelector('meta[name="description"]');
                if (meta) return meta.content;
                const ps = [...document.querySelectorAll('p')].filter(p => p.innerText.length > 30);
                return ps.slice(0, 6).map(p => p.innerText).join(' ');
            }""")

            # Price
            price = await page.evaluate("""() => {
                const candidates = [...document.querySelectorAll('[class*="price"],[class*="Price"]')];
                for (const el of candidates) {
                    const m = el.innerText.match(/[\d,]+/);
                    if (m) return m[0].replace(/,/g,'');
                }
                return '';
            }""")

            # Images
            images = await page.evaluate("""() => {
                const imgs = [...document.querySelectorAll('img')]
                    .map(i => i.src)
                    .filter(s => s.startsWith('http'));
                return imgs.slice(0, 5);
            }""")

            await browser.close()

            return {
                "name": name,
                "description": (description or "")[:2000],
                "price": str(price or ""),
                "images": images,
            }
    except Exception:
        return {"name": "", "description": "", "price": "", "images": []}
