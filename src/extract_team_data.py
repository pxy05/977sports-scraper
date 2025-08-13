import sys
import time
from playwright.async_api import async_playwright
import re
from src.progress_bar import print_progress_bar

def get_team_id(URL: str) -> str:
    return URL.rstrip('/').split('/')[-1].split('?')[0].split('#')[0]


def get_team_country(team_id: str) -> str:
    # team_id can just be URL aswell lol
    # Just more optimal reusing get_team_id
    split_string = team_id.split("/")
    split_string = split_string[-1].split("-")
    return split_string[len(split_string) - 2]

def get_team_uuid(URL: str) -> str:
    # URL can just be team_id aswell lol
    # Just more optimal reusing get_team_id
    return URL.split("-")[-1]

async def extract_team_data(URL: str, output: str = "output") -> None:

    XHR_PATTERN = re.compile(f"filterFormatLevel=ALL")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # Needs to be non-headless otherwise doesnt get past bot detection
        context = await browser.new_context()
        page = await context.new_page()

        all_players = []
        total_players = None

        async def handle_response(response):
            
            nonlocal total_players
            if XHR_PATTERN.search(response.url) and response.status == 200:
                try:
                    data = await response.json()

                    if total_players is None:
                        total_players = data.get("total", 0)

                    players = data.get("results", [])

                    # TODO
                    # Implement more optimal duplicate checking algorithm
                    for player_data in players:
                        if player_data not in all_players:
                            all_players.append(player_data)

                    
                    progress = len(all_players) / total_players if total_players else 0
                    # sys.stdout.write(f"\rProgress: {progress_bar_map[int(percentage_complete * 10)]}")


                    print_progress_bar(progress)
                except Exception as e:
                    print(f"Failed to parse JSON: {e}")

        page.on("response", handle_response)
        await page.goto(URL)

        #To bypass consent modals.
        #If one appears that hasnt been accounted for
        #please start an issue on: https://github.com/pxy05/sport-scraper/issues

        # Exit Disney Cookie Modal
        try:
            await page.wait_for_selector('button:has-text("Accept All")', timeout=2000)
            await page.click('button:has-text("Accept All")')
        except Exception:
            pass

        # Exit Cookie Modal

        try:
            await page.wait_for_selector('button:has-text("ALL")', timeout=2000)
            await page.click('button:has-text("ALL")')
        except Exception:
            pass

        # Click on ALL players
        # TODO
        # Include flag for different Tournaments e.g. # ALL, INTL, T20...

        try:
            await page.wait_for_selector('text="ALL"', timeout=500)
            await page.click('text="ALL"')
        except Exception:
            pass



        while total_players is None or len(all_players) < total_players:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(0.5)

        await browser.close()
        sys.stdout.write("\n")
        return all_players
    
    