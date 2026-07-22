"""
Centralized configuration for the Trolley Tracker system.

Every other script imports its settings from here instead of hardcoding
values, and this module is the ONLY place that reads the .env file.
That way, changing the DB filename, MQTT broker, admin credentials, etc.
never requires touching the actual application code.
"""
import os
from dotenv import load_dotenv

# Load variables from the .env file in the project root into the
# process environment (does nothing if .env is missing, so scripts
# still work with the defaults below).
load_dotenv()

# Absolute path to the project root (this file lives in shared/, one level down)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Database ---------------------------------------------------------
# If DB_NAME in .env is a bare filename (the normal case), resolve it
# against the project root so every script — regardless of which
# subfolder it lives in or which directory it's launched from — points
# at the exact same database file. An absolute path in .env is left as-is.
_db_name_raw = os.getenv("DB_NAME", "trolley.db")
DB_NAME = _db_name_raw if os.path.isabs(_db_name_raw) else os.path.join(PROJECT_ROOT, _db_name_raw)

# --- MQTT ---------------------------------------------------------------
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "airport/trolleys")

# --- Default admin account (used only to seed the users table) --------
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_ROLE = os.getenv("ADMIN_ROLE", "admin")

# --- Streamlit ------------------------------------------------------------
# These names match Streamlit's own environment variable convention, so if
# you `export` the .env file into your shell before running
# `streamlit run app.py`, Streamlit will bind to this port/address on its
# own. They're also exposed here in case a script wants to read them.
STREAMLIT_SERVER_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
STREAMLIT_SERVER_ADDRESS = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")
