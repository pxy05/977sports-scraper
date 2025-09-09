import requests
import json
from playwright.async_api import async_playwright
import re
from src.utils import *

async def extract_match_data(url: str, output_file: str = None):
    html = await fetch_page(url)
    match = re.search(r'<pre.*?>(.*?)</pre>', html, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        match = re.search(r'<body.*?>(.*?)</body>', html, re.DOTALL)
        if match:
            json_str = match.group(1).strip()
        else:
            raise ValueError("Could not extract JSON from HTML")
    data = json.loads(json_str)
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    return data
