from src.gmap_spider import Spider



s = Spider()
print(s.crawl("developers in Bangalore", max_results=20))