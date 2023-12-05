from src.spider import Spider
import pandas as pd
import asyncio


s = Spider()
places = asyncio.run(s.crawl("developers in Lahore", max_results=60, min_rating=4))

df = pd.DataFrame(data=places)
df.to_csv("data.csv",index=False)

