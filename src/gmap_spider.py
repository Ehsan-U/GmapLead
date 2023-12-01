from base64 import b64decode
import json
from urllib.parse import quote_plus, urlparse, parse_qs
from httpx import Client, HTTPError
from playwright_stealth import stealth_sync
from playwright.sync_api import sync_playwright
from src.gmap_parser import parse
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import os
from dataclasses import asdict

load_dotenv(dotenv_path='../.env')
from src.models import Response
from src.logger import logger



class Spider():
    """
    Spider class for crawling Google Maps search results.

    Attributes:
    - map_url (str): The base URL for Google Maps search.
    - proxy (str): The proxy server to be used for requests.

    Methods:
    - __init__(): Initializes the Spider object.
    - handle_request(route): Handles the intercepted requests during crawling.
    - search(query: str) -> Optional[Tuple]: Performs a search on Google Maps.
    - paginate(next_xhr_url: str) -> Optional[Tuple[Response, str]]: Fetches the next page of search results.
    - crawl(query: str, max_results=20) -> List[Dict]: Crawls Google Maps search results for a given query.
    """
    MAP_URL = "https://www.google.com/maps/search/{}"
    ZYTE_ENDPOINT = os.getenv("ZYTE_ENDPOINT")
    ZYTE_API_KEY = os.getenv("ZYTE_API_KEY")


    def __init__(self, proxy: bool = False):
        """
        Initializes the Spider object.
        """
        self.proxy = proxy
        self.xhr_url = []
        self.places_count = 0


    def handle_request(self, route):
        """
        Handles the intercepted requests during crawling.

        Args:
        - route: The intercepted request route.
        """
        request = route.request
        if 'search?tbm=map' in request.url:
            self.xhr_url.append(request.url)
        route.continue_()


    def search(self, query: str) -> Optional[Tuple]:
        """
        Performs a search on Google Maps.

        Args:
        - query (str): The search query.

        Returns:
        - Optional[Tuple]: A tuple containing the response and the URL for the next page of search results.
        """
        logger.info(f"Searching: {query}")

        url = self.MAP_URL.format(quote_plus(query))
        self.source = url

        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True).new_context()
            page = browser.new_page()
            stealth_sync(page)

            page.route("**/*", self.handle_request)
            page.goto(url)
            page.focus, "//h1[text()='Results']/ancestor::div[contains(@aria-label, 'Results for')]"

            while True:
                page.wait_for_timeout(2000)
                last_element = page.locator("//a[contains(@href, '/maps/place')]").last
                last_element.scroll_into_view_if_needed()
                if self.xhr_url:
                    return Response(status=200, url=self.source, text=page.content()), self.xhr_url.pop()
                
        return None, None


    def paginate(self, next_xhr_url: str) -> Optional[Tuple[Response, str]]:
        """
        Fetches the next page of search results.

        Args:
        - next_xhr_url (str): The URL for the next page of search results.

        Returns:
        - Optional[Tuple[Response, str]]: A tuple containing the response and the URL for the next page of search results.
        """
        logger.info(f"Page {round(self.places_count / 20)}")

        try:
            with Client() as client:
                if self.proxy and self.ZYTE_ENDPOINT and self.ZYTE_API_KEY:
                    response = client.post(
                        self.ZYTE_ENDPOINT,
                        auth=(self.ZYTE_API_KEY, ""),
                        json={
                            "url": next_xhr_url,
                            "httpResponseBody": True,
                            "httpRequestMethod": "GET"
                        },
                    )
                    http_response_body = b64decode(response.json()["httpResponseBody"]).decode()
                else:
                    response = client.get(next_xhr_url)
                    http_response_body = response.text
            if response.status_code != 200:
                raise HTTPError
        except Exception as e:
            logger.error(f"Error occurred while fetching: {next_xhr_url}\n {e}")
            return None, None
        
        if '/*""*/' in http_response_body:
            json_obj = json.loads(http_response_body.strip('/*""*/'))

            current_page_value = self.places_count
            next_page_value = self.places_count + 20

            # 8i20 8i40 8i60
            next_page_url = json_obj['u'].replace(f"8i{current_page_value}", f"8i{next_page_value}")
            ech = int(parse_qs(urlparse(next_page_url).query)['ech'][0])
            next_page_url = next_page_url.replace(f"ech={ech}", f"ech={ech + 1}")

            return Response(status=200, url=self.source, text=json_obj['d']), next_page_url
        else:
            return Response(status=404, url=self.source, text=None), None
        

    def crawl(self, query: str, max_results=20) -> List[Dict]:
        """
        Crawls Google Maps search results for a given query.

        Args:
        - query (str): The search query.
        - max_results (int): The maximum number of results to retrieve. Default is 20.

        Returns:
        - List[Dict]: A list of dictionaries representing the search results.
        """
        _output = []
        response, next_xhr_url = self.search(query)

        while (len(_output) < max_results) or (next_xhr_url is not None):
            places = parse(response)
            if not places:
                break
            _output.extend(places)
            self.places_count += 20
            response, next_xhr_url = self.paginate(next_xhr_url)

        return [asdict(place) for place in _output]



