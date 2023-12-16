import json
import re
from typing import Dict, List, Tuple, AnyStr
from urllib.parse import urldefrag
from httpx import Response
from parsel import Selector
from collections import namedtuple

from src.models import Place, SocialPatterns
from src.utils import safe_get


class ResponseWrapper:
    """
    A wrapper class for HTTP responses.

    Attributes:
        response (Response): The original HTTP response object.
        selector (Selector): The selector object for parsing the response text.
        url (str): The URL of the response.

    Methods:
        get_complete_address(place: List) -> Dict: Returns the complete address information for a place.
        places() -> List[Place]: Parses the response and returns a list of Place objects.
    """

    NOT_ALLOWED_DOMAINS = ["facebook.com", "twitter.com", "linkedin.com", "instagram.com", "tiktok.com", "youtube.com"]


    def __init__(self, response: Response):
        self.response = response
        self.selector = Selector(response.text)
        self.url = str(response.url)


    def __repr__(self):
        return f"ResponseWrapper({self.response})"


    def __str__(self):
        return f"ResponseWrapper({self.response})"


    def get_complete_address(self, place: List) -> Dict:
        """
        Returns the complete address information for a place.

        Args:
            place (List): The place data.

        Returns:
            Dict: The complete address information.

        """
        ward = safe_get(place, -1, 183, 1, 0)
        street = safe_get(place, -1, 183, 1, 1)
        city = safe_get(place, -1, 183, 1, 3)
        postal_code = safe_get(place, -1, 183, 1, 4)
        state = safe_get(place, -1, 183, 1, 5)
        country_code = safe_get(place, -1, 183, 1, 6)

        result = {
            'ward': ward,
            'street': street,
            'city': city,
            'postal_code': postal_code,
            'state': state,
            'country_code': country_code
        }

        return result


    def places(self) -> List[Place]:
        """
        Parses the response and returns a list of Place objects.

        Returns:
            List[Place]: The list of Place objects.

        """
        places = []
        
        text = self.response.text

        if '/*""*/' in text:
            json_obj = json.loads(text.strip('/*""*/'))
            text = json_obj['d']

        if not text.startswith(")]}'"):
            initialization_state_part = text.split(';window.APP_INITIALIZATION_STATE=')[1]
            app_initialization_state = initialization_state_part.split(';window.APP_FLAGS')[0]

            text = json.loads(app_initialization_state)[3][2]
            

        text = text[4:]  # remove )]}' from the start (its present in both cases)
        data = json.loads(text)

        for place in data[0][1][1:]:

            place_attributes = {
                'id': safe_get(place, -1, 78),
                'name': safe_get(place, -1, 11),
                'desc': safe_get(place, -1, 32, 1, 1),
                'reviews': safe_get(place, -1, 4, 8),
                'website': safe_get(place, -1, 7, 0),
                'owner': safe_get(place, -1, 57, 1),
                'main_category': safe_get(place, -1, 13, 0),
                'categories': safe_get(place, -1, 13),
                'rating': safe_get(place, -1, 4, 7),
                'phone': safe_get(place, -1, 178, 0, 0),
                'address': safe_get(place, -1, 18),
                'detailed_address': self.get_complete_address(place),
                'timezone': safe_get(place, -1, 30),
                'gmap_link': self.url
            }

            places.append(Place(**place_attributes))

        return places



    def links(self, size: int = 1) -> List:
        """
        Extracts links from the response.

        Args:
            size: The number of google search results for which links will be returned.

        Returns:
            A list of extracted links.
        """
        values = self.selector.xpath("//div[@id='main']//h3/ancestor::a/@href").getall()

        valid_links = [
            urldefrag(value).url
            for value in values
            if not any(domain in value for domain in self.NOT_ALLOWED_DOMAINS) and '.pdf' not in value
        ][:size]

        return valid_links
    

    def extract_emails(self) -> List:
        """
        Extracts emails from the response.

        Returns:
            A mapping of extracted emails.
        """
        email_regx = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return set(re.findall(email_regx, self.response.text))


    def extract_social_networks(self) -> Dict:
        """
        Extracts social network profiles from the response.

        Returns:
            A mapping of social network and profile.
        """
        social_links = {
            "facebook": None,
            "twitter": None,
            "linkedin": None,
            "instagram": None,
            "youtube": None,
            "pinterest": None,
        }
        
        social_patterns = {
            "facebook": SocialPatterns.FACEBOOK.value,
            "twitter": SocialPatterns.TWITTER.value,
            "linkedin": SocialPatterns.LINKEDIN.value,
            "instagram": SocialPatterns.INSTAGRAM.value,
            "youtube": SocialPatterns.YOUTUBE.value,
            "pinterest": SocialPatterns.PINTEREST.value
        }

        links = set(self.selector.xpath("//a/@href").getall())

        for link in links:
            for network, pattern in social_patterns.items():
                if re.search(pattern, link):
                    social_links[network] = link
                    break
                
        return social_links

