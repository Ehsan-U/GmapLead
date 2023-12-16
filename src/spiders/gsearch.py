
import os
from urllib.parse import urlencode, urlparse
from src.models import Place
from typing import List, Tuple
from dataclasses import asdict

from src.http_requests import Zyte_AsyncRequest
from src.http_response import ResponseWrapper
from src.models import Lead
from src.logger import logger



class GsearchSpider:
    """
    Class for scraping contact information (emails and social networks) from websites
    using Google Search and Zyte API.
    """

    BASE_URL = "https://www.google.com/search?"
    ZYTE_API_KEY = os.getenv("ZYTE_API_KEY")
    CONTACT_DORK = 'site:{} (inurl:contact OR inurl:about OR inurl:info OR inurl:reach-us OR inurl:reach_us) ("contact" OR "get in touch" OR "reach us" OR "contact us" OR "about us")'


    async def make_request(self, url) -> ResponseWrapper:
        """
        Sends an asynchronous GET request to a specified URL using Zyte API and parses the response.

        Args:
            url: The target URL for the request.

        Returns:
            A `ResponseWrapper` object containing the parsed response.
        """
        response = await Zyte_AsyncRequest(zyte_api_key=self.ZYTE_API_KEY, url=url, method="GET").process_request()
        return response
    

    async def search_contacts(self, domain: str) -> Tuple:
        """
        Searches Google Search for contact information (emails and social networks) on a specific domain.

        Args:
            domain: The domain name to search for contact information.

        Returns:
            A tuple containing:
                A list of extracted email addresses.
                A dictionary of extracted social network links with their corresponding platforms.
        """
        logger.info(f"Searching contacts for {domain}")
        emails, social_networks = [], {}

        params = {
            "q": self.CONTACT_DORK.format(domain),
            "num": 10,
            "hl": "en",
            "start": 0,
        }
        url = self.BASE_URL + urlencode(params)

        response = await self.make_request(url)
        if response:
            links = response.links(size=1)
            for link in links:
                response = await self.make_request(url=link)
                emails = response.extract_emails()
                social_networks = response.extract_social_networks()
        
        return (emails, social_networks)
            

    async def crawl(self, places: List[Place]) -> List[Lead]:
        """
        Crawls a list of `Place` objects and extracts contact information for each.

        Args:
            places: A list of `Place` objects containing website URLs.

        Returns:
            A list of `Lead` objects populated with place information and extracted contacts.
        """
        leads = []

        for place in places:
            if place.website is None:
                continue

            domain = urlparse(place.website).netloc.lstrip("www.")
            contacts = await self.search_contacts(domain)

            lead = Lead(
                **asdict(place),
                emails = ", ".join(contacts[0]),
                **contacts[-1]
            )

            logger.info(f"Lead: \n\n{lead}")
            leads.append(lead)
        
        return leads