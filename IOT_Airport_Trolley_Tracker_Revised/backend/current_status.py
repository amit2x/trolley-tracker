import sqlite3
from datetime import datetime, timedelta

# Connect to database
conn = sqlite3.connect("trolley.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get latest record of each trolley
cursor.execute("""
SELECT t1.*
FROM trolley_tracking t1
JOIN (
    SELECT trolley_id, MAX(timestamp) AS latest_time
    FROM trolley_tracking
    GROUP BY trolley_id
) t2
ON t1.trolley_id = t2.trolley_id
AND t1.timestamp = t2.latest_time
ORDER BY t1.trolley_id;
""")

rows = cursor.fetchall()

print("=" * 80)
print(f"{'Trolley':<12} {'Zone':<10} {'RSSI':<8} {'Status':<15} {'Timestamp'}")
print("=" * 80)

for row in rows:

    trolley_id = row["trolley_id"]
    zone = row["zone"]
    rssi = row["rssi"]
    status = row["status"]
    timestamp = row["timestamp"]

    # Determine OFFLINE dynamically
    last_seen = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

    if datetime.now() - last_seen > timedelta(minutes=5):
        current_status = "OFFLINE"
    else:
        current_status = status

    print(
        f"{trolley_id:<12} "
        f"{zone:<10} "
        f"{rssi:<8} "
        f"{current_status:<15} "
        f"{timestamp}"
    )

print("=" * 80)

conn.close()