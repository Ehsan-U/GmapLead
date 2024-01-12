from src.gmap import GmapSpider
import asyncio
from dotenv import load_dotenv

load_dotenv()


gmap = GmapSpider()
places = asyncio.run(gmap.crawl("Developers in Lahore", max_results=20))