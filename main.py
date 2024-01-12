import json
import os
from src.gmap import GmapSpider
import asyncio
from dotenv import load_dotenv

load_dotenv()

gmap = GmapSpider()
places = asyncio.run(gmap.crawl("Developers in Lahore", max_results=20))

os.makedirs("output", exist_ok=True)
with open("output/places.json", 'w') as f:
    json.dump(places, f, ensure_ascii=False)