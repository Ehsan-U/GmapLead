from src.gmap_spider import Spider



s = Spider(proxy=True)
print(s.crawl("developers in Bangalore"))