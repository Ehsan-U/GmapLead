from pprint import pprint 
import time
from urllib.parse import quote_plus
import random
import hrequests
from parsel import Selector
from gmap_parser import parse
from typing import Optional, Tuple, List

from models import Response, Place
from logger import logger



class Spider():
    """
    Spider class for crawling Google Maps search results and extracting places information.
    """

    map_url = "https://www.google.com/maps/search/{}"


    def __init__(self):
        self.xhr_url = []
        self.session = hrequests.Session(
            browser=random.choice(['chrome', 'firefox']),
            os=random.choice(['win', 'lin', 'mac'])
        )
        self.concurrent_requests = 3


    async def handle_request(self, route):
        """
        Handles the intercepted requests and appends the next page XHR URL to the list.
        """
        request = route.request
        if 'search?tbm=map' in request.url:
            self.xhr_url.append(request.url)
        await route.continue_()


    def search(self, query: str) -> Optional[Tuple]:
        """
        Performs a search on Google Maps for the given query and returns the response and next page XHR URL.

        Args:
            query (str): The search query.

        Returns:
            tuple: A tuple containing the response object and the next page XHR URL.
        """
        logger.info(f"Searching: {query}")

        url = self.map_url.format(quote_plus(query))

        with self.session.render(url='https://www.google.com/', mock_human=True, headless=True) as page:
            browser = page.page

            page._call_wrapper(browser.route, "**/*", self.handle_request)
            page._call_wrapper(page._goto, url)
            page._call_wrapper(browser.focus, "//h1[text()='Results']/ancestor::div[contains(@aria-label, 'Results for')]")

            while True:
                time.sleep(2)
                last_element = browser.locator("//a[contains(@href, '/maps/place')]").last
                page._call_wrapper(last_element.scroll_into_view_if_needed)
                if self.xhr_url:
                    return Response(status=200, text=page.content), self.xhr_url.pop()


    @staticmethod
    def err_handler(req, err):
        """
        Error handler for hrequests.map.

        Args:
            req (hrequests.Request): The request object.
            err (Exception): The exception object.
        """
        logger.error(f"Error occurred while fetching: {req.url}\n {err}")


    def get_places(self, response: Response) -> List[Place]:
        """
        Extracts the places information from the response.

        Args:
            response (Response): The response object.

        Returns:
            list: A list of parsed places information.
        """
        logger.info("Getting places")

        places = Selector(response.text).xpath("//a[contains(@href, '/maps/place')]/@href").getall()
        reqs = [self.session.async_get(place) for place in places]
        resps = hrequests.map(
            reqs, 
            size=self.concurrent_requests, 
            timeout=60, 
            exception_handler=self.err_handler
        )
        return [parse(resp) for resp in resps]


    def crawl(self, query: str):
        """
        Crawls Google Maps search results for the given query and prints the places information.

        Args:
            query (str): The search query.
        """
        response, next_xhr_url = self.search(query)
        places = self.get_places(response)
        pprint(places)




s = Spider()
s.crawl("developers in Bangalore")

