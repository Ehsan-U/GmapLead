from src.gmap_spider import Spider
import pandas as pd
import asyncio


s = Spider(proxy=True)
places = asyncio.run(s.crawl("developers in Bangalore", max_results=100))


