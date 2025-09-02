from anyio import sleep
from src.utils import fetch_page, write_to_file, verify_link
from src.extract_team_data import extract_team_data, get_team_id, get_team_country, get_team_uuid
from src.extract_player_data import extract_player_data
from src.progress_bar import print_progress_bar
import json

'''
Using sleep between each player info retrieval.

Sleep times between players tested:
10 seconds - Successful
'''



async def team_data(URL: str, output: str = "output") -> None:
    if not verify_link(URL, "team"):
        print("\033[91mError: Invalid team URL. It should start with 'https://www.espncricinfo.com/team/' or 'https://www.espncricinfo.com/cricketers/team/' and be followed by the team name only (no extra slashes).\033[0m")
        return

    team_id = get_team_id(URL).replace("-", "_")
    team_country = get_team_country(URL)


    if output == "output":
        output = team_id

    print(f"Output will be saved to: {output}")
    print(f"Scraping team: {team_id}")

    all_players = await extract_team_data(URL, output)

    print(f"Output saved to: {output}.json")

    print(f"Task Completed: Collected all {len(all_players)} players from {team_country}.")
    

    write_to_file(all_players, "json", output)


async def player_data(URL: str, individual_player: bool = False, output: str = "output") -> None:

    if individual_player:
        player_data = await extract_player_data(URL, True)
        if output == "output":
            output = player_data[0].get("player_id")
        write_to_file(player_data, "json", output)


async def team_full_data(URL: str, output: str = "output", existing_team_data: str = None, existing_player_data: str = None) -> None:
    # existing_team_data is just the path to the JSON file containing team data (literally just a list of team members links and ids)
    # existing_player_data is just the path to the JSON file containing player data (already scraped data)
    dissected_url = URL.strip().split('/')
    if not verify_link(URL, "team"):
        print("\033[91mError: Invalid team URL. It should start with 'https://www.espncricinfo.com/team/' or 'https://www.espncricinfo.com/cricketers/team/' and be followed by the team name only (no extra slashes).\033[0m")
        return
    #dissected_url has array structure like ['https:', '', 'www.espncricinfo.com', 'team', 'united-arab-emirates-27']
    print(f"Scraping players from: {dissected_url[-1]}")

    if dissected_url[3] != "cricketers":
        URL = f"https://www.espncricinfo.com/cricketers/team/{dissected_url[-1]}"
    
    


    if existing_team_data: #if existing team members list then use it
        with open(existing_team_data, "r", encoding="utf-8") as f:
            team_json = json.load(f)

    if existing_player_data and not existing_team_data: # if existing player data was already scraped then finish off the job
        with open(existing_player_data, "r", encoding="utf-8") as f:
            team_json = json.load(f)

    if not existing_player_data and not existing_team_data:
        team_json = await extract_team_data(URL, output)

    index = 0

    for player in team_json:
        index+=1
        player_id = str(player.get("objectId"))
        player_data = await extract_player_data(player_id, False)
        player["full_data"] = player_data
        print_progress_bar(index / len(team_json), True)
        write_to_file(team_json, "json", output) # save the updated team JSON after each player is processed so save if anything interrupts v annoying
        await sleep(5)

async def page(url: str, output: str = "output") -> None:
    page_html = await fetch_page(url)
    write_to_file(page_html, "html", output)

