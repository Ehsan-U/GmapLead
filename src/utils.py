from dataclasses import dataclass
from enum import Enum
from typing import Optional


@dataclass
class Response:
    status: int
    url: str
    text: str


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


def get_rating_enum(user_rating: float) -> Optional[int]:
    try:
        user_rating = float(user_rating)
        mapping = {
            1.0: Rating.NULL.value,
            2.0: Rating.TWO.value,
            2.5: Rating.TWO_HALF.value,
            3.0: Rating.THREE.value,
            3.5: Rating.THREE_HALF.value,
            4.0: Rating.FOUR.value,
            4.5: Rating.FOUR_HALF.value
        }
        return mapping.get(user_rating, None)
    except Exception:
        return None