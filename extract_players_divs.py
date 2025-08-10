import json
from bs4 import BeautifulSoup

with open('players-divs.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

players = []

for div in soup.select('div.ds-flex.ds-p-4.ds-flex-row'):
    player = {}
    # 1. href to the player's page (from first a)
    a1 = div.select_one('a.ds-flex')
    player['href'] = a1['href'] if a1 and a1.has_attr('href') else ''
    # 2. src url to their image (from img inside first a)
    img = a1.select_one('img') if a1 else None
    player['img_src'] = img['src'] if img and img.has_attr('src') else ''
    # 3. name (from title in second a)
    a2 = div.select_one('div.ds-flex-col a[title]')
    player['name'] = a2['title'] if a2 and a2.has_attr('title') else ''
    players.append(player)

with open('players-divs-parsed.json', 'w', encoding='utf-8') as f:
    json.dump(players, f, indent=2, ensure_ascii=False)

print(f"Extracted {len(players)} players to players-divs-parsed.json")
