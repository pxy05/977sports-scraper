import time
from playwright.async_api import async_playwright
import re
from src.utils import write_to_file\

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

async def extract_team_data(URL: str, output: str = "output", full:bool = False) -> None:

    if full:

        team_id = get_team_id(URL)
        team_country = get_team_country(URL)


        if output == "output":
            output = team_id

        print(f"Output will be saved to: {output}")
        print(f"Scraping team:{team_id}")


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
                print(f"Response URL: {XHR_PATTERN.search(response.url)}")
                try:
                    data = await response.json()

                    if total_players is None:
                        total_players = data.get("total", 0)
                        print(f"Total players to collect: {total_players}")

                    players = data.get("results", [])

                    # TODO
                    # Implement more optimal duplicate checking algorithm
                    for p_data in players:
                        if p_data not in all_players:
                            all_players.append(p_data)

                    print(f"Collected {len(all_players)}/{total_players} players so far")

                except Exception as e:
                    print(f"Failed to parse JSON: {e}")

        page.on("response", handle_response)
        await page.goto(URL)

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

            
        if full:
            team_id = get_team_id(URL)
            team_country = get_team_country(URL)


            if output == "output":
                output = team_id

            print(f"Output will be saved to: {output}")
            print(f"Scraping team:{team_id}")

            print(f"Task Completed: Collected all {len(all_players)} players from {team_country}.")
            await browser.close()

            write_to_file(all_players, "json", output)
