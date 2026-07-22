#MY New Updates Comming soon.

<div align="center">

# ✈️ IoT-Based Airport Trolley Tracking System

**Real-Time BLE & MQTT Based Smart Airport Trolley Monitoring**

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![MQTT](https://img.shields.io/badge/MQTT-Mosquitto-green)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightblue)
![License](https://img.shields.io/badge/License-Educational-orange)

</div>

> **IoT-Based Real-Time Airport Trolley Tracking and Monitoring System**

An IoT solution that tracks airport trolleys using **ESP32 BLE devices**, **MQTT**, **Python**, **SQLite**, and a **Streamlit dashboard**. The system enables airport staff to monitor trolley availability in real time while allowing passengers to view available trolleys in their selected zone.

---

# ✨ Project Highlights

- Real-time BLE-based trolley tracking
- MQTT-based communication
- Automatic trolley status detection using RSSI
- SQLite-based data storage
- Staff Dashboard
- Passenger Portal
- Zone-wise trolley availability
- Automatic offline detection
- Live dashboard updates

---

# Use Case

Airport trolleys are frequently misplaced across terminals, making them difficult for airport staff to locate and causing inconvenience for passengers.

This project provides a real-time IoT-based solution that continuously monitors trolley locations using BLE beacons and displays their availability through a web dashboard. Staff can efficiently manage trolley distribution, while passengers can identify available trolleys in their designated zones.

---

# System Workflow

1. ESP32 BLE Beacons advertise trolley information.
2. ESP32 BLE Scanner receives advertisements.
3. Scanner publishes trolley data to the Mosquitto MQTT Broker.
4. `backend/backend.py` subscribes to MQTT messages.
5. Incoming data is processed and stored in SQLite.
6. RSSI values determine trolley status.
7. Trolleys without updates for more than 5 minutes are marked OFFLINE.
8. Streamlit displays current trolley information.

---

# Project Structure

```text
trolley-tracker/
│
└── IOT_AIRPORT_TROLLEY_TRACKER_REVISED/
    │
    ├── backend/
    │   ├── backend.py
    │   ├── database.py
    │   ├── setup_users.py
    │   ├── current_status.py
    │   ├── history_view.py
    │   ├── clear_old_data.py
    │   └── test.py
    │
    ├── frontend/
    │   └── app.py
    │
    └── README.md
```

## Folder Responsibilities

### backend/
Contains the business logic, MQTT communication, SQLite operations, offline detection, database utilities, and helper scripts.

### frontend/
Contains the Streamlit web application used by airport staff and passengers.

---

# System Architecture

```text
        BLE Advertisement
+-------------------------------+
|     ESP32 BLE Beacon          |
+-------------------------------+
               │
               ▼
+-------------------------------+
|     ESP32 BLE Scanner         |
+-------------------------------+
               │
      Measures RSSI & Zone
               │
               ▼
       Creates JSON Payload
               │
               ▼
+-------------------------------+
|   Mosquitto MQTT Broker       |
+-------------------------------+
               │
               ▼
+-------------------------------+
|      backend/backend.py       |
|-------------------------------|
| • Receives MQTT messages      |
| • Parses JSON                 |
| • Determines trolley status   |
| • Stores records in SQLite    |
| • Marks offline trolleys      |
+-------------------------------+
               │
               ▼
+-------------------------------+
|       SQLite Database         |
+-------------------------------+
               │
               ▼
+-------------------------------+
|     frontend/app.py           |
|-------------------------------|
| • Staff Dashboard             |
| • Passenger Portal            |
+-------------------------------+
```

---

# 🛠️ Technology Stack

| Category | Technology |
|----------|------------|
| Programming Language | Python 3.x |
| Hardware | ESP32 |
| Wireless Communication | Bluetooth Low Energy (BLE) |
| Messaging Protocol | MQTT |
| MQTT Broker | Mosquitto |
| Database | SQLite |
| Web Framework | Streamlit |
| Data Processing | Pandas |

---

# Module Description

## Backend

### `backend.py`
- Subscribes to MQTT messages from the Mosquitto broker.
- Parses incoming JSON payloads.
- Determines trolley status based on RSSI values.
- Stores trolley data in the SQLite database.
- Periodically marks inactive trolleys as **OFFLINE**.

### `database.py`
- Creates the SQLite database.
- Creates the `trolley_tracking` table if it does not already exist.

### `setup_users.py`
- Creates the `users` and `passengers` tables.
- Inserts sample staff and passenger records.

### `current_status.py`
- Retrieves and displays the latest status of every trolley.

### `history_view.py`
- Displays the latest 1000 historical trolley records.

### `clear_old_data.py`
- Removes all trolley tracking records from the database.

### `test.py`
- Displays the database schema for debugging and verification.

---

## Frontend

### `app.py`
Provides the Streamlit web application, including:

- Staff Login
- Passenger Login
- Staff Dashboard
- Passenger Portal
- Zone-wise trolley filtering
- Live trolley status monitoring

---

# 🗄️ Database

## trolley_tracking

| Column | Type |
|---|---|
| id | INTEGER |
| trolley_id | TEXT |
| zone | TEXT |
| rssi | INTEGER |
| status | TEXT |
| timestamp | TEXT |

## users

| Column | Type |
|---|---|
| username | TEXT |
| password | TEXT |
| role | TEXT |

## passengers

| Column | Type |
|---|---|
| username | TEXT |
| pnr | TEXT |
| name | TEXT |
| flight_number | TEXT |
| scheduled_time | TEXT |
| gate | TEXT |

---

# MQTT Message Format

```json
{
  "trolley_id":"T-001",
  "zone":"ZONE_A",
  "rssi":-45
}
```

---

# RSSI Status Logic

| Condition | Status |
|-----------|--------|
| RSSI > -99 | ACTIVE |
| RSSI <= -99 | WEAK_SIGNAL |
| RSSI = -999 | OUT_OF_RANGE |
| No update for 5 minutes | OFFLINE |

---

# Requirements

- Python 3.x
- Mosquitto MQTT Broker
- ESP32 BLE Beacon
- ESP32 BLE Scanner
- SQLite (database created automatically during setup)

---

# 🚀 Installation

```bash
git clone https://github.com/amit2x/trolley-tracker.git
cd trolley-tracker
cd IOT_AIRPORT_TROLLEY_TRACKER_REVISED
```

Install dependencies

```bash
pip install streamlit pandas paho-mqtt schedule
```

Start Mosquitto

```bash
mosquitto
```

Create the database (first time only)

```bash
python backend/database.py
```

Running this script automatically creates the `trolley.db` SQLite database if it does not already exist.

Create sample users

```bash
python backend/setup_users.py
```

Run backend

```bash
python backend/backend.py
```

Run dashboard

```bash
streamlit run frontend/app.py
```

The Streamlit dashboard will be available at:

```text
http://localhost:8501
```

---

# Default Credentials

Staff

- Username: admin
- Password: admin123

Passenger

- Username: userid
- PNR: PNR12345

---

# 🔮 Future Improvements

- Password hashing
- Role-based access control
- MQTT authentication
- REST API integration
- Docker support
- Cloud database integration
- Dashboard analytics
- Push notifications

---

# Project Background

Developed as an internship project at the Airports Authority of India (AAI), Netaji Subhas Chandra Bose International Airport, Kolkata.

---

# 📄 License

This project is intended for educational and internship purposes.
