import sqlite3
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.config import DB_NAME

# Create/connect to database file
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()
# Create table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS trolley_tracking (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        trolley_id  TEXT,
        zone        TEXT,
        rssi        INTEGER,
        status      TEXT,
        timestamp   TEXT
    )
""")

conn.commit()
print("Database created successfully!")
# Insert a fake trolley ping
cursor.execute("""
    INSERT INTO trolley_tracking 
    (trolley_id, zone, rssi, status, timestamp)
    VALUES (?, ?, ?, ?, ?)
""", ("T-003", "ZONE_A", -46, "ACTIVE", "2026-06-10 19:41:00"))

conn.commit()
print("Data inserted!")

# Read it back
cursor.execute("SELECT * FROM trolley_tracking")
rows = cursor.fetchall()

for row in rows:
    print(row)
conn.close()