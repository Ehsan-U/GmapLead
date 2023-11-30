from dataclasses import dataclass



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