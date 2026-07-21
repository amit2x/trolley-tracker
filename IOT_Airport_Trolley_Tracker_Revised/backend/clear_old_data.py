import sqlite3

conn = sqlite3.connect("trolley.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM trolley_tracking")
conn.commit()
conn.close()

print("Old data cleared!")