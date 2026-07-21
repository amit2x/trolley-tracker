import sqlite3

conn = sqlite3.connect("trolley.db")
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

# Insert sample admin user
cursor.execute("""
    INSERT OR IGNORE INTO users (username, password, role)
    VALUES ('admin', 'admin123', 'admin')
""")

# Insert sample passenger
cursor.execute("""
    INSERT OR IGNORE INTO passengers (username, pnr, name, flight_number, scheduled_time, gate)
    VALUES ('userid', 'PNR12345', 'USERNAME', 'AI-202', '2026-06-25 18:30:00', 'Gate 14')
""")

conn.commit()
conn.close()
print("Tables created and sample data inserted!")
