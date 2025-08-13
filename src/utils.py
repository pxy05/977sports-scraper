import time
import json
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


def write_to_file(data, filetype: str, filename: str = "output") -> bool:

    if filetype == "json":
        try:
            with open(f"{filename}.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                return True
        except Exception as e:
            print(f"Error writing JSON to {filename}: {e}")
            return False

    if filetype == "html":
        try:
            with open(f"{filename}.html", 'w', encoding='utf-8') as f:
                f.write(data)
                return True
        except Exception as e:
            print(f"Error writing HTML to {filename}: {e}")
            return False
    return False

async def fetch_page(url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url)

        # try:
        #     try:
        #         await page.wait_for_selector('button:has-text("Accept All")', timeout=5000)
        #         await page.click('button:has-text("Accept All")')
        #     except Exception:
        #         try:
        #             await page.wait_for_selector('button:has-text("Accept")', timeout=5000)
        #             await page.click('button:has-text("Accept")')
        #         except Exception:
        #             pass
        # except Exception:
        #     pass

        scrolls = 3
        for _ in range(scrolls):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(0.5)

        html_content = await page.content()

        await browser.close()
        
        return html_content

