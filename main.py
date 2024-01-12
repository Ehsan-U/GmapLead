import json
import os
from src.gmap import GmapSpider
import asyncio
from dotenv import load_dotenv

load_dotenv()

gmap = GmapSpider()
places = asyncio.run(gmap.crawl("Developers in Lahore", max_results=20))

output_dir = "output"
os.makedirs(output_dir, exist_ok=True)
with open(f"{output_dir}/places.json", 'w') as f:
    json.dump(places, f, ensure_ascii=False)