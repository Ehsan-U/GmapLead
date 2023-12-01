from src.gmap_spider import Spider
import pandas as pd


s = Spider(proxy=True)
places = s.crawl("developers in Bangalore", max_results=150)


df = pd.DataFrame(places)
df.to_csv('places.csv', index=False)
