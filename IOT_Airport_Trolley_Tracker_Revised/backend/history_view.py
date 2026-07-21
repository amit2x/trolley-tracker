import sqlite3

conn = sqlite3.connect("trolley.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
SELECT
    trolley_id,
    zone,
    rssi,
    status,
    timestamp
FROM trolley_tracking
ORDER BY timestamp DESC
LIMIT 1000;
""")

rows = cursor.fetchall()

print("=" * 80)
print(f"{'Trolley':<12} {'Zone':<10} {'RSSI':<8} {'Status':<15} {'Timestamp'}")
print("=" * 80)

for row in rows:
    print(
        f"{row['trolley_id']:<12}"
        f"{row['zone']:<10}"
        f"{row['rssi']:<8}"
        f"{row['status']:<15}"
        f"{row['timestamp']}"
    )

print("=" * 80)
print(f"Total records displayed: {len(rows)}")

conn.close()