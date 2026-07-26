import paho.mqtt.client as mqtt
import sqlite3
import json
from datetime import datetime
import schedule
import time
import threading
import sys
import os

# Make the project root importable so `shared` resolves no matter where
# this script is launched from.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.config import DB_NAME, MQTT_BROKER, MQTT_PORT, MQTT_TOPIC

# Database setup
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
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

    offline_conn = sqlite3.connect(DB_NAME)
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
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    # Wrapped in try/except so one malformed or unexpected message
    # (e.g. bad JSON from a manual mosquitto_pub test, a flaky device,
    # or buggy firmware) gets logged and skipped instead of crashing
    # the entire backend process — without this, a single bad message
    # would take down data collection for every trolley until the
    # script is manually restarted.
    try:
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

    except json.JSONDecodeError:
        print(f"Ignored malformed message (not valid JSON): {msg.payload!r}")
    except KeyError as e:
        print(f"Ignored message missing required field {e}: {msg.payload!r}")
    except Exception as e:
        print(f"Unexpected error handling message, skipping: {e}")


# MQTT setup
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT)


# Run offline check every 60 seconds
schedule.every(60).seconds.do(check_offline)


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


thread = threading.Thread(target=run_schedule, daemon=True)
thread.start()

client.loop_forever()