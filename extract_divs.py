from bs4 import BeautifulSoup

with open("output.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

# Find all divs with the exact class
target_class = "ds-flex ds-p-4 ds-flex-row ds-space-x-4 ds-border-line ds-border-b odd:ds-border-r last:ds-border-none"
divs = soup.find_all("div", class_=target_class)

with open("players-divs.txt", "w", encoding="utf-8") as out:
    for div in divs:
        out.write(str(div))
        out.write("\n\n")

print(f"Extracted {len(divs)} divs to players-divs.txt")