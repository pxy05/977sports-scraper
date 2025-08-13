from src.utils import fetch_page, write_to_file
from src.extract_team_data import extract_team_data, get_team_id, get_team_country, get_team_uuid
from src.extract_player_data import extract_player_data
import json

async def extract_team_players(URL: str, output: str = "output", full:bool = False) -> None:

    team_id = get_team_id(URL)
    team_country = get_team_country(URL)


    if output == "output":
        output = team_id

    print(f"Output will be saved to: {output}")
    print(f"Scraping team:{team_id}")

    all_players = await extract_team_data(URL, output, full)

    if full:
        for player in all_players:
            slug = player.get("slug")
            id = player.get("objectId")
            player_url = f"https://www.espncricinfo.com/player/{slug}-{id}"
            data_url = f"https://stats.espncricinfo.com/ci/engine/player/{id}.html?class=11;template=results;type=allround"
            player_data = await extract_player_data(player_url, False, output)
            player["full_data"] = player_data

    print(f"Output will be saved to: {output}")
    print(f"Scraping team:{team_id}")

    print(f"Task Completed: Collected all {len(all_players)} players from {team_country}.")
    

    write_to_file(all_players, "json", output)


async def player_data(URL: str, individual_player: bool = False, output: str = "output") -> None:

    if individual_player:
        player_data = await extract_player_data(URL)
        if output == "output":
            output = player_data[0].get("player_id")
        write_to_file(player_data, "json", output)


async def extract_team_full_data(URL: str, output: str = "output") -> None:
    

    return

async def extract_page(url: str, output: str = "output") -> None:
    page_html = await fetch_page(url)
    write_to_file(page_html, "html", output)

