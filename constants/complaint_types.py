"""
The type of complaints in any Bhawan
"""

ELECTRIC = "ele"
TOILET = "toi"
CARPENTRY = "car"
CLEANING = "cle"
MESS = "mes"
OTHER = "oth"
FEEDBACK = "fdb"

COMPLAINT_TYPES = (
    (ELECTRIC, "Electric"),
    (TOILET, "Toilet"),
    (CARPENTRY, "Carpentry"),
    (CLEANING, "Cleaning"),
    (MESS, "Mess"),
    (FEEDBACK, "feedback"),
    (OTHER, "Other"),
)
COMPLAINT_TYPES_MAP = {
    'ELECTRIC': ELECTRIC,
    'TOILET': TOILET,
    'CARPENTRY': CARPENTRY,
    'CLEANING': CLEANING,
    'MESS': MESS,
    'FEEDBACK': FEEDBACK,
    'OTHER': OTHER,
}
