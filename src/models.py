from dataclasses import dataclass
from enum import Enum



@dataclass
class Place:
    place_id: str
    place_name: str
    place_desc: str
    place_reviews: str
    place_website: str
    place_owner: str
    place_main_category: str
    place_categories: str
    place_rating: str
    place_phone: str
    place_address: str
    place_detailed_address: str
    place_timezone: str
    place_gmap_link: str



# this represent page button index
class Rating(Enum):
    TWO = 1 
    TWO_HALF = 2
    THREE = 3
    THREE_HALF = 4
    FOUR = 5
    FOUR_HALF = 6
    NULL = None


class MapSelectors(Enum):
    RATING_BTN = "//button[@aria-label='Rating']"
    RATING_INDEX = "//div[@role='menuitemradio' and @data-index='{}']"
    RESULTS = "//h1[text()='Results']/ancestor::div[contains(@aria-label, 'Results for')]"
    PLACES = "//a[contains(@href, '/maps/place')]"