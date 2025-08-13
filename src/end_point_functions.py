from src.utils import fetch_page, write_to_file
from src.extract_team_data import extract_team_data, get_team_id, get_team_country, get_team_uuid
from src.extract_player_data import extract_player_data
import json

async def team_data(URL: str, output: str = "output") -> None:

    team_id = get_team_id(URL).replace("-", "_")
    team_country = get_team_country(URL)


    if output == "output":
        output = team_id

    print(f"Output will be saved to: {output}")
    print(f"Scraping team: {team_id}")

    all_players = await extract_team_data(URL, output)

    # if no_write: #WHAT IT CHANGED???
    #     for player in all_players:
    #         slug = player.get("slug")
    #         id = player.get("objectId")
            # player_url = f"https://www.espncricinfo.com/player/{slug}-{id}"
            # data_url = f"https://stats.espncricinfo.com/ci/engine/player/{id}.html?class=11;template=results;type=allround"
            

    print(f"Output saved to: {output}.json")

    print(f"Task Completed: Collected all {len(all_players)} players from {team_country}.")
    

    write_to_file(all_players, "json", output)


async def player_data(URL: str, individual_player: bool = False, output: str = "output") -> None:

    if individual_player:
        player_data = await extract_player_data(URL)
        if output == "output":
            output = player_data[0].get("player_id")
        write_to_file(player_data, "json", output)


async def team_full_data(URL: str, output: str = "output") -> None:
    team_json = await extract_team_data(URL, output)
    temp = []

    index = 0
    for player in team_json:
        if index < 5:
            temp.append(player)
        index += 1

    team_json = temp

    for player in team_json:
        player_id = str(player.get("objectId"))
        player_data = await extract_player_data(player_id, True)
        player["full_data"] = player_data
    write_to_file(team_json, "json", output)

async def page(url: str, output: str = "output") -> None:
    page_html = await fetch_page(url)
    write_to_file(page_html, "html", output)

