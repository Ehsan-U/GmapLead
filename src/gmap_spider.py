import asyncio
from base64 import b64decode
import json
from urllib.parse import quote_plus, urlparse, parse_qs
from httpx import AsyncClient, HTTPError
from playwright_stealth import stealth_async
from playwright.async_api import async_playwright
from src.gmap_parser import parse
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import os
from aiolimiter import AsyncLimiter
from dataclasses import asdict

load_dotenv(dotenv_path='../.env')
from src.utils import Response, get_rating_enum
from src.logger import logger


class Spider():
    """
    Spider class for crawling Google Maps search results.
    """

    MAP_URL = "https://www.google.com/maps/search/{}"
    ZYTE_ENDPOINT = os.getenv("ZYTE_ENDPOINT")
    ZYTE_API_KEY = os.getenv("ZYTE_API_KEY")


    def __init__(self, proxy: bool = False, rate_limit: int = 100):
        """
        Initializes the Spider object.

        Args:
        - proxy (bool): Flag indicating whether to use a proxy. Default is False.
        """

        self.proxy = proxy
        self.xhr_url = []
        self.places_count = 0
        self.rate_limit = AsyncLimiter(max_rate=rate_limit)


    async def handle_request(self, route):
        """
        Handles the intercepted requests during crawling.

        Args:
        - route: The intercepted request route.
        """

        request = route.request
        if 'search?tbm=map' in request.url:
            self.xhr_url.append(request.url)
        await route.continue_()


    async def search(self, query: str, min_rating: float) -> Optional[Tuple]:
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

        try:
            async with async_playwright() as p:
                browser = await p.firefox.launch(headless=True)
                page = await browser.new_page()
                await stealth_async(page)

                await page.route("**/*", self.handle_request)
                await page.goto(url)

                idx = get_rating_enum(min_rating)
                if idx:
                    await page.wait_for_selector("//button[@aria-label='Rating']")
                    await page.locator("//button[@aria-label='Rating']").first.click()

                    await page.locator(f"//div[@role='menuitemradio' and @data-index='{idx}']").click()
                    await page.wait_for_timeout(2000)

                await page.focus("//h1[text()='Results']/ancestor::div[contains(@aria-label, 'Results for')]")

                for _ in range(3):
                    last_element = page.locator("//a[contains(@href, '/maps/place')]").last
                    await last_element.scroll_into_view_if_needed()
                    await page.wait_for_timeout(2000)
                    content = await page.content()
                    if self.xhr_url:
                        return Response(status=200, url=self.source, text=content), self.xhr_url.pop()
                
                logger.warning("XHR not found")
                return Response(status=200, url=self.source, text=content), None
            
        except Exception as e:
            logger.error(e)
        
        return None, None


    async def fetch(self, client: AsyncClient, url: str) -> Optional[Response]:
        """
        Fetches the content of a given URL using an HTTP GET request.

        Args:
            client (AsyncClient): The HTTP client used to make the request.
            url (str): The URL to fetch.

        Returns:
            Response: The HTTP response containing the fetched content.

        Raises:
            HTTPError: If the response status code is not 200.
        """
        
        try:
            async with self.rate_limit:
                if self.proxy and self.ZYTE_ENDPOINT and self.ZYTE_API_KEY:

                    response = await client.post(
                        self.ZYTE_ENDPOINT,
                        auth=(self.ZYTE_API_KEY, ""),
                        json={
                            "url": url,
                            "httpResponseBody": True,
                            "httpRequestMethod": "GET"
                        },
                    )
                    http_response_body = b64decode(response.json()["httpResponseBody"]).decode()
                else:

                    response = await client.get(url)
                    http_response_body = response.text

                if response.status_code != 200:
                    raise HTTPError
            
        except Exception as e:
            logger.error(f"Error occurred while fetching: {url}\n {e}")
            raise e
        else:
            if '/*""*/' in http_response_body:
                json_obj = json.loads(http_response_body.strip('/*""*/'))
                return Response(status=200, url=self.source, text=json_obj['d'])


    def _create_task(self, client: AsyncClient, next_xhr_url: str) -> asyncio.Task:
        """
        Creates a task for fetching the next page of search results.

        Args:
        - next_xhr_url (str): The URL for the next page of search results.
        """

        # 8i20 8i40 8i60
        next_page_url = next_xhr_url.replace(f"8i20", f"8i{self.places_count}")
        ech = int(parse_qs(urlparse(next_page_url).query)['ech'][0])
        next_page_url = next_page_url.replace(f"ech={ech}", f"ech={ech + 1}")

        return asyncio.create_task(self.fetch(client, next_page_url))


    async def crawl(self, query: str, max_results: int = 20, min_rating: float = 0) -> List[Dict]:
        """
        Crawls Google Maps search results for a given query.

        Args:
        - query (str): The search query.
        - max_results (int): The maximum number of results to retrieve. Default is 20.

        Returns:
        - List[Dict]: A list of dictionaries representing the search results.
        """

        response, next_xhr_url = await self.search(query, min_rating)
        places = parse(response)

        if places and next_xhr_url:
            tasks = []
            async with AsyncClient() as client:
                while self.places_count < max_results:
                    self.places_count += 20

                    task = self._create_task(client, next_xhr_url)
                    tasks.append(task)

                    logger.info(f"Total places: {self.places_count}, Page: {round(self.places_count / 20)}")

                responses = await asyncio.gather(*tasks, return_exceptions=True)
                for resp in responses:
                    if resp and isinstance(resp, Response):
                        places.extend(parse(resp))
            
        return [asdict(place) for place in places]



