from src.spiders.gmap import GmapSpider
import json
import asyncio
from dotenv import load_dotenv

load_dotenv()

import time
start_time = time.perf_counter()

gmap = GmapSpider()
places = asyncio.run(gmap.crawl("Real estate in London", max_results=100))
print(places)
end_time = time.perf_counter()
print(f"Time taken: {end_time-start_time}")


