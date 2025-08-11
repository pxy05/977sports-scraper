from src.utils import fetch_page, write_to_file
from bs4 import BeautifulSoup

async def extract_team_players(url: str, output: str = "output") -> list:

    html = await fetch_page(url)
    soup = BeautifulSoup(html, "html.parser")

    target_class = "ds-flex ds-p-4 ds-flex-row ds-space-x-4 ds-border-line ds-border-b odd:ds-border-r last:ds-border-none"
    divs = soup.find_all("div", class_=target_class)

    players = []

    for div in divs:
        player = {}

        a1 = div.select_one('a.ds-flex')
        player['href'] = a1['href'] if a1 and a1.has_attr('href') else ''

        img = a1.select_one('img') if a1 else None
        player['img_src'] = img['src'] if img and img.has_attr('src') else ''

        a2 = div.select_one('div.ds-flex-col a[title]')
        player['name'] = a2['title'] if a2 and a2.has_attr('title') else ''
        players.append(player)

    await write_to_file(players, "json", output)

    print(f"Extracted {len(players)} players to {output}.json")

async def extract_player_data(player: str, individual_player: bool = False, output: str = "output") -> None:
    
    if individual_player:
        html = await fetch_page(player)
        write_to_file(html, "html", output)



async def extract_team_full_data():
    return

async def extract_page(url: str, output: str = "output") -> None:
    page_html = await fetch_page(url)
    write_to_file(page_html, "html", output)

