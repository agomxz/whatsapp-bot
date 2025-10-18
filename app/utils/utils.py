import re
from app.constants.coincidences import VEHICLE_KEYWORDS


def is_vehicle_query(message: str) -> bool:
    """Check if a message is related to vehicle queries."""
    # Remove special characters and convert to lowercase
    clean_msg = re.sub(r"[^\w\s]", "", message.lower())
    # Check if any vehicle keyword is in the message
    return any(keyword in clean_msg.split() for keyword in VEHICLE_KEYWORDS)
