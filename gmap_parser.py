
import json
from models import Place



def safe_get(data, *args):
    """
    Safely get the value from the data object
    """
    for arg in args:
        try:
            data = data[arg]
        except (IndexError, TypeError, KeyError):
            return None
    return data


def get_complete_address(data):
    """
    Get the complete address from the data object
    """
    ward = safe_get(data, 6, 183, 1, 0)
    street = safe_get(data, 6, 183, 1, 1)
    city = safe_get(data, 6, 183, 1, 3)
    postal_code = safe_get(data, 6, 183, 1, 4)
    state = safe_get(data, 6, 183, 1, 5)
    country_code = safe_get(data, 6, 183, 1, 6)

    result = {
        'ward': ward,
        'street': street,
        'city': city,
        'postal_code': postal_code,
        'state': state,
        'country_code': country_code
    }
    return result


def parse(response):
    """
    Parse the response of a Google Maps place
    """
    if response and response.status_code == 200:
        initialization_state_part = response.text.split(';window.APP_INITIALIZATION_STATE=')[1]
        app_initialization_state = initialization_state_part.split(';window.APP_FLAGS')[0]
        
        json_str = json.loads(app_initialization_state)[3][6]
        if json_str.startswith(")]}'"):
            json_str = json_str[4:]
        data = json.loads(json_str)
        
        place_id = safe_get(data, 6, 78)
        place_name = safe_get(data, 6, 11)
        place_desc =  safe_get(data, 6, 32, 1, 1)
        place_reviews = safe_get(data, 6, 4, 8)
        place_website = safe_get(data, 6, 7, 0)
        place_owner = safe_get(data, 6, 57, 1)
        place_main_category = safe_get(data, 6, 13, 0)
        place_categories = safe_get(data, 6, 13)
        place_rating = safe_get(data, 6, 4, 7)
        place_phone = safe_get(data, 6, 178, 0, 0)
        place_address = safe_get(data, 6, 18)
        place_detailed_address = get_complete_address(data)
        place_timezone = safe_get(data, 6, 30)
        place_gmap_link = response.url

        return Place(
            place_id=place_id,
            place_name=place_name,
            place_desc=place_desc,
            place_reviews=place_reviews,
            place_website=place_website,
            place_owner=place_owner,
            place_main_category=place_main_category,
            place_categories=place_categories,
            place_rating=place_rating,
            place_phone=place_phone,
            place_address=place_address,
            place_detailed_address=place_detailed_address,
            place_timezone=place_timezone,
            place_gmap_link=place_gmap_link
        )


