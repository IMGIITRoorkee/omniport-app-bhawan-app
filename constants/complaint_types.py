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
    (TOILET, "Washroom"),
    (CARPENTRY, "Carpentry"),
    (CLEANING, "Cleaning"),
    (MESS, "Mess"),
    (FEEDBACK, "feedback"),
    (OTHER, "Others"),
)
COMPLAINT_TYPES_MAP = {
    'ELECTRIC': ELECTRIC,
    'WASHROOM': TOILET,
    'CARPENTRY': CARPENTRY,
    'CLEANING': CLEANING,
    'MESS': MESS,
    'FEEDBACK': FEEDBACK,
    'OTHERS': OTHER,
}
