from dataclasses import dataclass
from enum import Enum



@dataclass
class Place:
    id: str = None
    title: str = None
    # desc: str = None
    reviews: str = None
    website: str = None
    owner: str = None
    main_category: str = None
    categories: str = None
    rating: str = None
    phone: str = None
    address: str = None
    detailed_address: str = None
    timezone: str = None
    status: str = None
    coordinates: dict = None
    hours: list = None


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
