"""
The type of complaints in any Bhawan
"""

ELECTRIC = "ele"
TOILET = "toi"
CARPENTRY = "car"
CLEANING = "cle"
MESS = "mes"
OTHER = "oth"

COMPLAINT_TYPES = (
    (ELECTRIC, "Electric"),
    (TOILET, "Toilet"),
    (CARPENTRY, "Carpentry"),
    (CLEANING, "Cleaning"),
    (MESS, "Mess"),
    (OTHER, "Other"),
)
COMPLAINT_TYPES_MAP = {
    'ELECTRIC': ELECTRIC,
    'TOILET': TOILET,
    'CARPENTRY': CARPENTRY,
    'CLEANING': CLEANING,
    'OTHER': OTHER,
}
