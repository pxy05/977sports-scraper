import time
import json
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

def verify_link(url: str, type: str) -> bool:
    #dissected_url has array structure like ['https:', '', 'www.espncricinfo.com', 'team', 'united-arab-emirates-27']

    team_prefixes = [
        "https://www.espncricinfo.com/team/",
        "https://www.espncricinfo.com/cricketers/team/"
    ]

    match type:
        case "team":
            url_split = url.split("/")
            if len(url_split) > 6 or len(url_split) < 5:
                return False
            return any(
                url.startswith(prefix) and 
                url[len(prefix):].strip("/") != "" and 
                "/" not in url[len(prefix):].strip("/")
                for prefix in team_prefixes
            )
        case "player":
            return url.startswith("https://www.espncricinfo.com/cricketers/")
        case _:
            return False

def process_player(player: dict) -> dict:
            slug = player.get("slug")
            id = player.get("objectId")
            player_url = f"https://www.espncricinfo.com/player/{slug}-{id}"
            data_url = f"https://stats.espncricinfo.com/ci/engine/player/{id}.html?class=11;template=results;type=allround"



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

        #To bypass consent modals.
        #If one appears that hasnt been accounted for
        #please start an issue on: https://github.com/pxy05/sport-scraper/issues

        try:
            await page.wait_for_selector('button:has-text("Consent")', timeout=2000)
            await page.click('button:has-text("Consent")')
        except Exception:
            pass



        scrolls = 3
        for _ in range(scrolls):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(0.5)

        html_content = await page.content()

        await browser.close()
        
        return html_content

