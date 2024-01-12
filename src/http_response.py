import json
from typing import Dict, List
from httpx import Response
from parsel import Selector

from src.models import Place
from src.utils import safe_get


class ResponseWrapper:
    """
    A wrapper class for HTTP responses.

    Attributes:
        response (Response): The original HTTP response object.

    Methods:
        get_complete_address(place: List) -> Dict: Returns the complete address information for a place.
        places() -> List[Place]: Parses the response and returns a list of Place objects.
    """


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
    

    @staticmethod
    def get_open_hours(place):
        ls = []
        elements = safe_get(place, -1, 34, 1) or []
        for element in elements:
            day, times = element[0], element[1]
            time = times[0] if times else None
            ls.append({'day': day, 'time':  time})
        return ls
    

    def places(self) -> List[Place]:
        """
        Parses the response and returns a list of Place objects.
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
                'title': safe_get(place, -1, 11),
                # 'desc': safe_get(place, -1, 32, 1, 1),
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
                'status': safe_get(place, -1, 34, 4, 4),
                'coordinates': {'latitude': safe_get(place, -1, 9, 2), 'longitude': safe_get(place, -1, 9, 3)},
                "hours": self.get_open_hours(place),
            }
            places.append(Place(**place_attributes))

        return places