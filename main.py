from src.spiders.gmap import GmapSpider
from src.spiders.gsearch import GsearchSpider
import json
import asyncio
from dotenv import load_dotenv

load_dotenv()


# gather business leads from Google Map
gmap = GmapSpider()
places = asyncio.run(gmap.crawl("Real estate in London", max_results=20))

# gather social links from Google Search
gsearch = GsearchSpider()
leads = asyncio.run(gsearch.crawl(places))


with open("data/output/data.json", 'w') as f:
    json.dump(leads, f)

