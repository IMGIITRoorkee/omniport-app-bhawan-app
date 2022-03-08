"""
The type of complaints in any Bhawan
"""

ALMIRAH_REPAIR = "almrep"
CHAIR = "cha"
STUDY_TABLE = "stutab"
TEA_TABLE = "teatab"
DOOR_REPAIR= "doorep"
PLASTER_REPAIR = "plaprep"
FLOOR_REPAIR = "florep"
WINDOW_REPAIR = "winrep"
SEEPAGE_IN_WALLS = "seep"
TERMITE_TREATMENT = "term"
WATER_LINE_LEAKAGE = "leak"
CEILING_FAN_REPAIR = "ceifanrep"
ELECTRIC_PANEL_REPAIR = "elepanrep"
LIGHT_POINT_REPAIR = "ligpoirep"
STREET_LIGHT_REPAIR = "strligrep"
SWITCH_BOARD_REPAIR = "swiboarep"
WIRING_REPAIR = "wirrep"
CHAMBER_CLEANING = "chacle"
GARBAGE_REMOVAL = "garrem"
GRASS_CUTTING = "gracut"
SANITIZATION = "san"
SEWER_LINE_CHOKE = "sewlincho"
HOT_WATER = "hotwat"
HOT_WATER_LINE_LEAKAGE = "hotwatleak"
WATER_OVERFLOWING = "watove"
LANDSCAPE_WORK = "lanwor"
TREE_BRANCHES_TRIMMING = "tretri"
TREES_REMOVAL = "remtre"
OTHER = "oth"


COMPLAINT_ITEMS = (
    (ALMIRAH_REPAIR , "Almirah Repair"),
    (CHAIR , "Chair"),
    (STUDY_TABLE , "Study Table"),
    (TEA_TABLE , "Tea Table"),
    (DOOR_REPAIR , "Door Repair"),
    (PLASTER_REPAIR , "Plaster Repair"),
    (FLOOR_REPAIR , "Floor Repair"),
    (WINDOW_REPAIR , "Window Repair"),
    (SEEPAGE_IN_WALLS , "Seepage in Walls"),
    (WATER_LINE_LEAKAGE , "Water Line Leakage"),
    (CEILING_FAN_REPAIR , "Ceiling Fan Repair"),
    (ELECTRIC_PANEL_REPAIR , "Electric Panel Repair"),
    (LIGHT_POINT_REPAIR , "Light Point Repair"),
    (STREET_LIGHT_REPAIR , "Street Light Repair"),
    (SWITCH_BOARD_REPAIR , "Switch Board Repair"),
    (WIRING_REPAIR , "wiring Repair"),
    (CHAMBER_CLEANING , "Chamber Cleaning"),
    (GARBAGE_REMOVAL , "Garbage Removal"),
    (GRASS_CUTTING , "Grass Cutting"),
    (SANITIZATION , "Sanitization"),
    (SEWER_LINE_CHOKE , "Sewer Line Choke"),
    (HOT_WATER , "Hot water"),
    (HOT_WATER_LINE_LEAKAGE , "Hot Water Line Leakage"),
    (WATER_OVERFLOWING , "Water Overflowing"),
    (LANDSCAPE_WORK , "Landscape Work"),
    (TREE_BRANCHES_TRIMMING , "Tree Branches Trimming"),
    (TREES_REMOVAL , "Trees Removal"),
    (OTHER, "Others")
)

COMPLAINT_ITEMS_MAP = {
    'ALMIRAH_REPAIR': ALMIRAH_REPAIR,
    'CHAIR': CHAIR,
    'STUDY_TABLE': STUDY_TABLE,
    'TEA_TABLE': TEA_TABLE,
    'DOOR_REPAIR': DOOR_REPAIR,
    'PLASTER_REPAIR': PLASTER_REPAIR,
    'FLOOR_REPAIR': FLOOR_REPAIR,
    'WINDOW_REPAIR': WINDOW_REPAIR,
    'SEEPAGE_IN_WALLS': SEEPAGE_IN_WALLS,
    'WATER_LINE_LEAKAGE': WATER_LINE_LEAKAGE,
    'CEILING_FAN_REPAIR': CEILING_FAN_REPAIR,
    'ELECTRIC_PANEL_REPAIR': ELECTRIC_PANEL_REPAIR,
    'LIGHT_POINT_REPAIR': LIGHT_POINT_REPAIR,
    'STREET_LIGHT_REPAIR': STREET_LIGHT_REPAIR,
    'SWITCH_BOARD_REPAIR': SWITCH_BOARD_REPAIR,
    'WIRING_REPAIR': WIRING_REPAIR,
    'CHAMBER_CLEANING': CHAMBER_CLEANING,
    'GARBAGE_REMOVAL': GARBAGE_REMOVAL,
    'GRASS_CUTTING': GRASS_CUTTING,
    'SANITIZATION': SANITIZATION,
    'SEWER_LINE_CHOKE': SEWER_LINE_CHOKE,
    'HOT_WATER': HOT_WATER,
    'HOT_WATER_LINE_LEAKAGE': HOT_WATER_LINE_LEAKAGE,
    'WATER_OVERFLOWING': WATER_OVERFLOWING,
    'LANDSCAPE_WORK': LANDSCAPE_WORK,
    'TREE_BRANCHES_TRIMMING': TREE_BRANCHES_TRIMMING,
    'TREES_REMOVAL': TREES_REMOVAL,
    'OTHER': OTHER,
}
