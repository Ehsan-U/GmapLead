from src.gmap_spider import Spider
import pandas as pd
import asyncio


s = Spider(proxy=True)
places = asyncio.run(s.crawl("developers in Bangalore", min_rating=4.5))

df = pd.DataFrame(data=places)
df.to_csv("data.csv",index=False)

