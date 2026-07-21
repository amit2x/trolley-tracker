import sqlite3

conn = sqlite3.connect("trolley.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(trolley_tracking)")
for row in cursor.fetchall():
    print(row)

conn.close()