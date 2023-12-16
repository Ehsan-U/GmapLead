from src.spiders.gmap import GmapSpider
from src.spiders.gsearch import GsearchSpider
import pandas as pd
import asyncio
from dotenv import load_dotenv

load_dotenv()


# gather business leads from Google Map
gmap = GmapSpider()
places = asyncio.run(gmap.crawl("resturants in Canada", max_results=20))

# gather social links from Google Search
gsearch = GsearchSpider()
places = asyncio.run(gsearch.crawl(places))

df = pd.DataFrame(data=places)
df.to_csv("data.csv",index=False)

