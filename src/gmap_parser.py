import json
from typing import List, Dict
from src.models import Place, Response



def safe_get(place, *args):
    """
    Safely retrieves a value from a nested dictionary.

    Args:
        place (dict): The dictionary to retrieve the value from.
        *args: Variable number of keys to access the nested values.

    Returns:
        The value retrieved from the nested dictionary, or None if any of the keys are not found.

    """
    for arg in args:
        try:
            place = place[arg]
        except (IndexError, TypeError, KeyError):
            return None
    return place


def get_complete_address(place: List) -> Dict:
    """
    Get the complete address from a place object.

    Args:
        place (List): The place object.

    Returns:
        Dict: A dictionary containing the complete address information, including ward, street, city, postal code, state, and country code.
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


def parse(response: Response) -> List[Place]:
    """
    Parse the response and extract the relevant information to create a list of Place objects.

    Args:
        response (Response): The response object containing the data to be parsed.

    Returns:
        List[Place]: A list of Place objects extracted from the response.
    """
    places = []
    
    text = response.text

    if not text.startswith(")]}'"):
        initialization_state_part = text.split(';window.APP_INITIALIZATION_STATE=')[1]
        app_initialization_state = initialization_state_part.split(';window.APP_FLAGS')[0]

        text = json.loads(app_initialization_state)[3][2] 
    
    text = text[4:] # remove )]}' from the start (its present in both cases)
    data = json.loads(text)

    for place in data[0][1][1:]:

        place_attributes = {
            'place_id': safe_get(place, -1, 78),
            'place_name': safe_get(place, -1, 11),
            'place_desc': safe_get(place, -1, 32, 1, 1),
            'place_reviews': safe_get(place, -1, 4, 8),
            'place_website': safe_get(place, -1, 7, 0),
            'place_owner': safe_get(place, -1, 57, 1),
            'place_main_category': safe_get(place, -1, 13, 0),
            'place_categories': safe_get(place, -1, 13),
            'place_rating': safe_get(place, -1, 4, 7),
            'place_phone': safe_get(place, -1, 178, 0, 0),
            'place_address': safe_get(place, -1, 18),
            'place_detailed_address': get_complete_address(place),
            'place_timezone': safe_get(place, -1, 30),
            'place_gmap_link': response.url
        }

        places.append(Place(**place_attributes))

    return places

