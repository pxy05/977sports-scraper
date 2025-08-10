'''
Extract All players' information from a team pages for espncricinfo

e.g. "https://www.espncricinfo.com/cricketers/team/nepal-33"
'''

from bs4 import BeautifulSoup
import json

with open("output.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

# Find all divs with the exact class
target_class = "ds-flex ds-p-4 ds-flex-row ds-space-x-4 ds-border-line ds-border-b odd:ds-border-r last:ds-border-none"
divs = soup.find_all("div", class_=target_class)

players = []

for div in divs:
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

with open('players-divs-parsed1.json', 'w', encoding='utf-8') as f:
    json.dump(players, f, indent=2, ensure_ascii=False)
print(f"Extracted {len(players)} players to players-divs-parsed1.json")
