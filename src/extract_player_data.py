from bs4 import BeautifulSoup
from src.utils import fetch_page
import re

async def extract_player_data(url: str, single_player: bool ):

    if "https" not in url:
        url = "https://stats.espncricinfo.com/ci/engine/player/" + url + ".html?class=11;template=results;type=allround"

    #class references the class in the URL .html?class=3;template=results;type=allround
    all_col_names = ["Heading" ,"Span", "Mat", "Runs", "HS", "Bat Av", "100", "Wkts", "BBI", "Bowl Av", "5", "Ct", "St", "Ave Diff"] #class=11
    T20_col_names = ["Heading" ,"Span", "Mat", "Runs", "HS", "Bat Av", "100", "Wkts", "BBI", "Bowl Av", "5", "Ct", "St", "Ave Diff"] #class=2 | T20 is same as "all" but god knows if that will ever change
    ODI_col_names = ["Heading" ,"Mat", "Runs", "HS", "Bat Av", "100", "Wkts", "BBI", "Bowl Av", "5", "Ct", "St", "Ave Diff"] #class=3

    class_id = None

    match = re.search(r'class=(\d+)', url)

    class_id = match.group(1)
    if class_id == "3":
        col_names = ODI_col_names
    elif class_id == "2":
        col_names = T20_col_names
    else:
        col_names = all_col_names

    html = await fetch_page(url)
    soup = BeautifulSoup(html, "html.parser")

    player_name_element = soup.find("a", href=re.compile(r"/ci/engine/player/\d+\.html"))
    player_name = "player_data"
    if player_name_element and player_name_element.text:
        parts = player_name_element.text.split("/")[2]
        parts = parts.split(" ")
        player_name = parts[1] + " " + parts[2]

    player_id_match = re.search(r'/player/(\d+)\.html', url)
    player_id = player_id_match.group(1) if player_id_match else None

    results = {
        "player_name": player_name,
        "player_id": player_id,
        "stats": {}
    }
    
    tables = soup.find_all("table", class_="engineTable")
    
    for table in tables:
        rows = table.find_all("tr", class_=["data1", "data2"])
        if len(rows) < 1:
            continue

        # Adjust col_names if table is wider
        if len(rows[0].find_all("td")) > len(col_names):
            for i in range(len(rows[0].find_all("td")) - len(col_names)):
                col_names.append(f"extra_{i}")

        for tr in rows:
            tds = tr.find_all("td")
            row = {}
            for i, td in enumerate(tds):
                col_val = td.get_text(strip=True)
                if col_val != "":
                    row[col_names[i]] = col_val

            if row and "Heading" in row:
                heading = row.pop("Heading")
                if heading not in results["stats"]:
                    results["stats"][heading] = []
                results["stats"][heading].append(row)
                
    for key in list(results["stats"].keys()):
        results["stats"][key] = [item for item in results["stats"][key] if len(item) >= 7]
        if not results["stats"][key]:
            del results["stats"][key]
    return results

