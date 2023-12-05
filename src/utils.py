from typing import Optional
from src.models import Rating



def get_rating_enum(user_rating: float) -> Optional[int]:
    """
    Converts a user rating to its corresponding enum value.

    Args:
        user_rating: The user rating to be converted.

    Returns:
        The corresponding enum value of the user rating, or None if the rating is not found in the mapping.
    """

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
    

def safe_get(place: dict, *args) -> Optional[str]:
    """
    Safely retrieves a value from a nested dictionary.

    Args:
        place: The dictionary to retrieve the value from.
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