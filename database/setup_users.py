import sqlite3
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.config import DB_NAME, ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_ROLE
from shared.auth import hash_password

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Users table — for admin/staff login
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        role     TEXT
    )
""")

# Passengers table — for passenger login
cursor.execute("""
    CREATE TABLE IF NOT EXISTS passengers (
        username        TEXT PRIMARY KEY,
        pnr             TEXT,
        name            TEXT,
        flight_number   TEXT,
        scheduled_time  TEXT,
        gate            TEXT
    )
""")

# Insert sample admin user (password is hashed before storage — never
# store plaintext passwords, even ones that only came from .env)
cursor.execute("""
    INSERT OR IGNORE INTO users (username, password, role)
    VALUES (?, ?, ?)
""", (ADMIN_USERNAME, hash_password(ADMIN_PASSWORD), ADMIN_ROLE))

# Insert sample passenger
cursor.execute("""
    INSERT OR IGNORE INTO passengers (username, pnr, name, flight_number, scheduled_time, gate)
    VALUES ('userid', 'PNR12345', 'USERNAME', 'AI-202', '2026-06-25 18:30:00', 'Gate 14')
""")

conn.commit()
conn.close()
print("Tables created and sample data inserted!")
