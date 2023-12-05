import asyncio
from urllib.parse import quote_plus, urlparse, parse_qs
from playwright_stealth import stealth_async
from playwright.async_api import async_playwright
from typing import Dict, List, Tuple
from dotenv import load_dotenv
import os
from dataclasses import asdict
from httpx import Response
import httpx

load_dotenv()
from src.utils import get_rating_enum
from src.logger import logger
from src.http_requests import ZYTE_REQUEST, AsyncRequest
from src.http_response import ResponseWrapper
from src.models import MapSelectors


class Spider():
    """
    Spider class for crawling and searching Google Maps data.
    """

    MAP_URL = "https://www.google.com/maps/search/{}"
    ZYTE_ENDPOINT = os.getenv("ZYTE_ENDPOINT")
    ZYTE_API_KEY = os.getenv("ZYTE_API_KEY")
    PLAYWRIGHT_TIMEOUT = 120*1000


    def __init__(self) -> None:
        """
        Initialize Spider object.
        """
        self.xhr_url = []
        self.places_count = 0


    async def handle_request(self, route) -> None:
        """
        Handle the intercepted requests during crawling.
        """
        request = route.request
        if 'search?tbm=map' in request.url:
            self.xhr_url.append(request.url)
        await route.continue_()


    async def search(self, query: str, min_rating: float) -> Tuple[ResponseWrapper, str]:
        """
        Searches for a query on Google Maps and returns the response.

        Args:
            query (str): The search query.
            min_rating (float): The minimum rating for the search results.

        Returns:
            The response wrapper object containing the search results, or None if an error occurred.
        """
        logger.info(f"Searching: {query}")

        url = self.MAP_URL.format(quote_plus(query))
        self.source = url
        try:
            async with async_playwright() as p:
                browser = await p.firefox.launch(headless=True, timeout=self.PLAYWRIGHT_TIMEOUT)
                page = await browser.new_page()
                await stealth_async(page)
                await page.route("**/*", self.handle_request)
                await page.goto(url, timeout=self.PLAYWRIGHT_TIMEOUT)

                idx = get_rating_enum(min_rating)
                if idx:
                    await page.wait_for_selector(MapSelectors.RATING_BTN.value)
                    await page.locator(MapSelectors.RATING_BTN.value).first.click()
                    await page.locator(MapSelectors.RATING_INDEX.value.format(idx)).click()
                    await page.wait_for_timeout(2000)

                await page.focus(MapSelectors.RESULTS.value)
                for _ in range(3):
                    last_element = page.locator(MapSelectors.PLACES.value).last
                    await last_element.scroll_into_view_if_needed()
                    await page.wait_for_timeout(2000)
                    content = await page.content()
                    if self.xhr_url:
                        return ResponseWrapper(
                            Response(
                                status_code=200, 
                                request=httpx.Client().build_request(url=self.source, method="GET"), 
                                text=content
                            )
                        ), self.xhr_url.pop()
                        
                logger.warning("XHR not found")
                return ResponseWrapper(
                    Response(
                        status_code=200, 
                        request=httpx.Client().build_request(url=self.source, method="GET"), 
                        text=content
                    )
                ), None
            
        except Exception as e:
            logger.error(e)

        return None, None


    def _create_task(self, next_xhr_url: str) -> asyncio.Task:
        """
        Create an asyncio task for processing the next XHR URL.

        Args:
            next_xhr_url: The next XHR URL.

        Returns:
            The created asyncio task.
        """
        next_page_url = next_xhr_url.replace(f"8i20", f"8i{self.places_count}")
        ech = int(parse_qs(urlparse(next_page_url).query)['ech'][0])
        next_page_url = next_page_url.replace(f"ech={ech}", f"ech={ech + 1}")
        
        request = ZYTE_REQUEST(zyte_api_key=self.ZYTE_API_KEY, url=next_page_url, async_mode=True)
        return asyncio.create_task(request.process_request())


    async def crawl(self, query: str, max_results: int = 20, min_rating: float = 0) -> List[Dict]:
        """
        Crawl Google Maps data based on the given query, maximum results, and minimum rating.

        Args:
            query: The search query.
            max_results: The maximum number of results to retrieve.
            min_rating: The minimum rating for the places.

        Returns:
            A list of dictionaries representing the crawled places.
        """
        response, next_xhr_url = await self.search(query, min_rating)
        places = response.places()

        if places and next_xhr_url:
            tasks = []
            while self.places_count < max_results:
                self.places_count += 20
                task = self._create_task(next_xhr_url)
                tasks.append(task)
                logger.info(f"Total places: {self.places_count}, Page: {round(self.places_count / 20)}")

            responses = await asyncio.gather(*tasks, return_exceptions=True)
            for resp in responses:
                if resp and isinstance(resp, ResponseWrapper):
                    places.extend(resp.places())
            
        return [asdict(place) for place in places]



