from dataclasses import dataclass
from enum import Enum



@dataclass
class Place:
    id: str = None
    name: str = None
    desc: str = None
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
    gmap_link: str = None
    


@dataclass
class Lead(Place):
    emails: list = None
    linkedin: str = None
    facebook: str = None
    instagram: str = None
    youtube: str = None
    twitter: str = None
    pinterest: str = None



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


class SocialPatterns(Enum):
    FACEBOOK = r"(?:facebook\.com|fb\.me)/(?:[A-Za-z0-9\.]+)"
    TWITTER = r"twitter\.com/(?:[A-Za-z0-9_]{1,15})"
    LINKEDIN = r"linkedin\.com/in/(?:[A-Za-z0-9_-]+\/)"
    INSTAGRAM = r"instagram\.com/(?:[A-Za-z0-9_\-.]+)"
    YOUTUBE = r"youtube\.com/(?:channel|user)/(?:[A-Za-z0-9_\-.]+)"
    PINTEREST = r"pinterest\.com/(?:[A-Za-z0-9_-]+\/)"