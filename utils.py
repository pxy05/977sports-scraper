from playwright.sync_api import sync_playwright
import time

def fetch_page(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        page = context.new_page()
        page.goto(url)

        scrolls = 10
        for _ in range(scrolls):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(3)

        html_content = page.content()

        browser.close()
        return html_content
