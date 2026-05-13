import pyodbc

# Global UI Constants
PRIMARY_BG = "#0D1425"
ACCENT = "#22c55e"
TEXT_COLOR = "white"

# Application State
is_guest = False
current_user_email = None

# Caches and Global Data Variables
generated_fixtures = []
simulated_2025_results = {}
TEAM_LOGO_CACHE = None
TEAM_RATING_CACHE = {}
TEAM_DEFAULTS_CACHE = {}
IMAGE_CACHE = {}

model_get_prediction = None
MODEL_IMPORT_ERROR = None

# Database Connections
try:
    conn = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};'
        'Server=DESKTOP-FGR06IV\\SQLEXPRESS;'
        'Database=UserSystem;'
        'Trusted_Connection=yes;'
        'Encrypt=no;'
        'TrustServerCertificate=yes;'
    )
    cursor = conn.cursor()
except Exception as e:
    print("Warning: Could not connect to UserSystem DB:", e)
    conn = None
    cursor = None

try:
    my_conn = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};'
        'Server=DESKTOP-FGR06IV\\SQLEXPRESS;'
        'Database=FootballDB;'
        'Trusted_Connection=yes;'
        'Encrypt=no;'
        'TrustServerCertificate=yes;'
    )
    my_cursor = my_conn.cursor()
except Exception as e:
    print("Warning: Could not connect to FootballDB:", e)
    my_conn = None
    my_cursor = None

TEAM_STADIUMS = {
    "Liverpool": "Anfield",
    "Man United": "Old Trafford",
    "Man City": "Etihad Stadium",
    "Arsenal": "Emirates Stadium",
    "Chelsea": "Stamford Bridge",
    "Tottenham": "Tottenham Hotspur Stadium",
    "Newcastle": "St James' Park",
    "West Ham": "London Stadium",
    "Burnley":"Truf Moor",
    "Everton":"Hill Dickinson",
    "Southampton":"St Mary's Stadium",
    "Wolves":"Molineux Stadium",
    "Sheffield":"Bramall Lane",
    "Watford":"Vicarage Road",
    "Bournemouth":"Dean Court",
    "Brentford":"Gtech Community Stadium",
    "Fulham":"Craven Cottage"
}

# Image Paths
INTRO_IMG1 = r"imag\main\page1.jpg"
INTRO_IMG2 = r"imag\main\page2.png"
INTRO_IMG3 = r"imag\main\page3.png"
INTRO_IMG4 = r"imag\main\page4.png"
LOGIN_IMG_PATH = r"imag\main\login.png"

IMAGES_DIR = r"imag\logo"
CHECK_ICON_PATH = IMAGES_DIR + r"\check.png"

import os
TEAM_IMAGE_FILES = {
    "Liverpool": os.path.join(IMAGES_DIR, "image5.jpeg"),
    "Manchester United": os.path.join(IMAGES_DIR, "image7.jpeg"),
    "Manchester City": os.path.join(IMAGES_DIR, "image11.jpeg"),
    "Arsenal": os.path.join(IMAGES_DIR, "image2.jpeg"),
    "Tottenham": os.path.join(IMAGES_DIR, "image6.jpeg"),
    "Chelsea": os.path.join(IMAGES_DIR, "image1.jpeg"),
    "Newcastle": os.path.join(IMAGES_DIR, "image10.jpeg"),
    "West Ham": os.path.join(IMAGES_DIR, "image12.jpeg"),
}
