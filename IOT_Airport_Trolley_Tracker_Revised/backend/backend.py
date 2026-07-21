import paho.mqtt.client as mqtt
import sqlite3
import json
from datetime import datetime
import schedule
import time
import threading

# Database setup
conn = sqlite3.connect("trolley.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS trolley_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trolley_id TEXT,
    zone TEXT,
    rssi INTEGER,
    status TEXT,
    timestamp TEXT
)
""")
conn.commit()


# Business logic
def determine_status(rssi):
    if rssi == -999:
        return "OUT_OF_RANGE"
    elif rssi > -99:
        return "ACTIVE"
    else:
        return "WEAK_SIGNAL"


def check_offline():
    print("Checking for offline trolleys...")

    offline_conn = sqlite3.connect("trolley.db")
    offline_cursor = offline_conn.cursor()

    offline_cursor.execute("""
        UPDATE trolley_tracking
        SET status = 'OFFLINE'
        WHERE timestamp < datetime('now', '-5 minutes')
        AND status != 'OFFLINE'
    """)

    offline_conn.commit()
    offline_conn.close()

    print("Offline check done!")


# MQTT callbacks
def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected to Mosquitto!")
    client.subscribe("airport/trolleys")


def on_message(client, userdata, msg):
    raw = msg.payload.decode()
    data = json.loads(raw)

    trolley_id = data["trolley_id"]
    zone = data["zone"]
    rssi = data["rssi"]

    status = determine_status(rssi)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO trolley_tracking
        (trolley_id, zone, rssi, status, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (trolley_id, zone, rssi, status, timestamp))

    conn.commit()

    print(f"Inserted : {trolley_id} | {zone} | {rssi} | {status} | {timestamp}")


# MQTT setup
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883)


# Run offline check every 60 seconds
schedule.every(60).seconds.do(check_offline)


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


thread = threading.Thread(target=run_schedule, daemon=True)
thread.start()

client.loop_forever()