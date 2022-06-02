"""
The type of rooms in any Bhawan
"""

TOTAL = "tot"
GUEST = "gue"
OFFICIAL = "off"
DAMP = "dam"

ROOM_TYPES = (
    (TOTAL, "Total Constructed Rooms"),
    (GUEST, "Guest Rooms"),
    (OFFICIAL, "Official Rooms"),
    (DAMP, "Damp Rooms")
)
ROOM_TYPES_MAP = {
    'TOTAL CONSTRUCTED ROOMS': TOTAL,
    'GUEST ROOMS': GUEST,
    'OFFICIAL ROOMS': OFFICIAL,
    'DAMP ROOMS': DAMP,
}
ROOM_TYPES_LIST = [
    TOTAL,
    GUEST,
    OFFICIAL,
    DAMP
]
