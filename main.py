from src.spiders.gmap import GmapSpider
from src.spiders.gsearch import GsearchSpider
import pandas as pd
import asyncio


gmap = GmapSpider()
places = asyncio.run(gmap.crawl("developers in Lahore", max_results=20))

df = pd.DataFrame(data=places)
df.to_csv("data.csv",index=False)

