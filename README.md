<div align="center">

# ✈️ IoT-Based Airport Trolley Tracking System

**Real-Time BLE & MQTT Based Smart Airport Trolley Monitoring**

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![MQTT](https://img.shields.io/badge/MQTT-Mosquitto-green)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightblue)
![License](https://img.shields.io/badge/License-Educational-orange)

</div>

An IoT solution that tracks airport trolleys using **ESP32 BLE devices**,
**MQTT**, **Python**, **SQLite**, and a **Streamlit dashboard**. Airport
staff can monitor trolley availability in real time, and passengers can
view available trolleys in their selected zone.

---

## ✨ Project Highlights

- Real-time BLE-based trolley tracking
- MQTT-based communication
- Automatic trolley status detection using RSSI
- SQLite-based data storage
- Staff Dashboard + Passenger Portal
- Zone-wise trolley availability
- Automatic offline detection
- Bcrypt-hashed staff passwords (no plaintext credentials in the DB)
- Centralized `.env`-driven configuration

---

## Use Case

Airport trolleys are frequently misplaced across terminals, making them
difficult for staff to locate and inconvenient for passengers. This
project continuously monitors trolley locations using BLE beacons and
displays their availability through a web dashboard, so staff can manage
distribution and passengers can find an available trolley in their zone.

---

## System Workflow

1. ESP32 BLE Beacons advertise trolley information.
2. An ESP32 BLE Scanner receives the advertisements and measures RSSI/zone.
3. The scanner publishes a JSON payload to the Mosquitto MQTT broker.
4. `backend/backend.py` subscribes to that MQTT topic.
5. Incoming pings are parsed and stored in SQLite.
6. RSSI values determine trolley status (`ACTIVE` / `WEAK_SIGNAL` / `OUT_OF_RANGE`).
7. A background job marks trolleys `OFFLINE` if no ping has arrived in 5 minutes.
8. The Streamlit dashboard (`frontend/app.py`) displays current trolley info.

---

## System Architecture

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

## 🛠️ Technology Stack

| Category | Technology |
|---|---|
| Programming Language | Python 3.x |
| Hardware | ESP32 |
| Wireless Communication | Bluetooth Low Energy (BLE) |
| Messaging Protocol | MQTT |
| MQTT Broker | Mosquitto |
| Database | SQLite |
| Web Framework | Streamlit |
| Data Processing | Pandas |
| Password Security | bcrypt |
| Config Management | python-dotenv |

---

## Project Structure

```text
trolley_tracker/
├── .env                  # your local config (never commit this)
├── .env.example          # template for .env — safe to commit
├── .gitignore
├── requirements.txt
├── README.md
├── shared/               # code used by both backend and frontend
│   ├── config.py         #   loads .env, exposes settings as constants
│   └── auth.py           #   bcrypt password hashing helpers
├── backend/
│   └── backend.py        # MQTT listener → writes pings into SQLite
├── frontend/
│   └── app.py            # Streamlit dashboard (staff + passenger login)
└── database/             # one-off / maintenance scripts
    ├── database.py        # creates trolley_tracking table + sample row
    ├── setup_users.py     # creates users/passengers tables, seeds admin login
    ├── clear_old_data.py  # wipes trolley_tracking
    ├── current_status.py  # prints latest status per trolley
    ├── history_view.py    # prints last 1000 tracking records
    └── test.py            # prints the trolley_tracking table schema
```

Every script under `backend/`, `frontend/`, and `database/` adds the
project root to `sys.path` and imports from `shared/`, so they can be run
from anywhere — the project root, their own subfolder, wherever — and
will always read the same `.env` and write to the same database file
(`shared/config.py` resolves `DB_NAME` to an absolute path under the
project root).

---

## Module Description

### `shared/config.py`
Loads `.env` via `python-dotenv` and exposes every setting (DB name, MQTT
broker info, admin credentials, Streamlit port) as constants that every
other script imports.

### `shared/auth.py`
Bcrypt password hashing helpers — `hash_password()` used when seeding the
admin account, `verify_password()` used to check a login attempt.

### `backend/backend.py`
- Subscribes to MQTT messages from the Mosquitto broker.
- Parses incoming JSON payloads.
- Determines trolley status based on RSSI values.
- Stores trolley data in the SQLite database.
- Periodically marks inactive trolleys as `OFFLINE`.

### `database/database.py`
Creates the SQLite database and the `trolley_tracking` table (if it
doesn't already exist), and inserts one sample row.

### `database/setup_users.py`
Creates the `users` and `passengers` tables, and seeds a sample staff
login (password stored as a bcrypt hash) and a sample passenger record.

### `database/current_status.py`
Retrieves and prints the latest status of every trolley.

### `database/history_view.py`
Prints the latest 1000 historical trolley records.

### `database/clear_old_data.py`
Removes all trolley tracking records from the database.

### `database/test.py`
Prints the `trolley_tracking` table schema — useful for debugging.

### `frontend/app.py`
Streamlit web app providing:
- Staff Login / Passenger Login
- Staff Dashboard (zone filter, live counts by status)
- Passenger Portal (zone-wise available trolleys)

---

## 🗄️ Database Schema

### `trolley_tracking`

| Column | Type |
|---|---|
| id | INTEGER (primary key, autoincrement) |
| trolley_id | TEXT |
| zone | TEXT |
| rssi | INTEGER |
| status | TEXT |
| timestamp | TEXT |

### `users`

| Column | Type |
|---|---|
| username | TEXT (primary key) |
| password | TEXT (bcrypt hash) |
| role | TEXT |

### `passengers`

| Column | Type |
|---|---|
| username | TEXT (primary key) |
| pnr | TEXT |
| name | TEXT |
| flight_number | TEXT |
| scheduled_time | TEXT |
| gate | TEXT |

---

## MQTT Message Format

```json
{
  "trolley_id": "T-001",
  "zone": "ZONE_A",
  "rssi": -45
}
```

## RSSI Status Logic

| Condition | Status |
|---|---|
| RSSI > -99 | ACTIVE |
| RSSI <= -99 | WEAK_SIGNAL |
| RSSI = -999 | OUT_OF_RANGE |
| No update for 5 minutes | OFFLINE |

---

## Requirements

- Python 3.x
- Mosquitto MQTT broker
- ESP32 BLE beacon + ESP32 BLE scanner (hardware side)
- Everything else installs via `requirements.txt`

## 🚀 Installation & Setup

```bash
pip install -r requirements.txt
```

The `.env` file holds every configurable value (DB filename, MQTT broker
info, default admin login, Streamlit port). Copy `.env.example` to `.env`
and edit it to fit your environment — nothing else needs to change.
`.gitignore` already excludes `.env` and `*.db` so secrets and local data
never get committed.

Start Mosquitto (if not already running):

```bash
mosquitto
```

### First-time setup (run once, from the project root)

```bash
python database/database.py       # creates trolley_tracking table + one sample row
python database/setup_users.py    # creates users/passengers tables + seeds admin login (password hashed with bcrypt)
```

> **Already ran an older flat-layout `setup_users.py` before this update?**
> Your `users` table may have a plaintext password in it from before
> hashing was added. Delete `trolley.db` and re-run the two commands above
> so the admin row gets recreated with a proper bcrypt hash. Old plaintext
> rows will simply fail to log in after this change (by design) rather
> than silently working.

### Running the system

```bash
python backend/backend.py         # MQTT listener that writes pings into the DB
streamlit run frontend/app.py     # dashboard (staff + passenger login)
```

The dashboard will be available at `http://localhost:8501` by default.

### Default Credentials

**Staff:** username `admin`, password `admin123` (or whatever you set as
`ADMIN_PASSWORD` in `.env`)

**Passenger:** username `userid`, PNR `PNR12345`

⚠️ Change `ADMIN_PASSWORD` in `.env` to a real password before deploying
anywhere beyond local testing.

---

## Utility / Debug Scripts

| Script | Purpose |
|---|---|
| `database/current_status.py` | Prints latest known status per trolley |
| `database/history_view.py` | Prints last 1000 tracking records |
| `database/clear_old_data.py` | Wipes the `trolley_tracking` table |
| `database/test.py` | Prints the `trolley_tracking` table schema |

---

## Configuration

All scripts import their settings from `shared/config.py`, which reads
`.env` via `python-dotenv`. Available variables:

| Variable | Default | Used by |
|---|---|---|
| `DB_NAME` | `trolley.db` | every script |
| `MQTT_BROKER` | `localhost` | `backend/backend.py` |
| `MQTT_PORT` | `1883` | `backend/backend.py` |
| `MQTT_TOPIC` | `airport/trolleys` | `backend/backend.py` |
| `ADMIN_USERNAME` | `admin` | `database/setup_users.py` |
| `ADMIN_PASSWORD` | `admin123` | `database/setup_users.py` |
| `ADMIN_ROLE` | `admin` | `database/setup_users.py` |
| `STREAMLIT_SERVER_PORT` | `8501` | Streamlit (export into shell env) |
| `STREAMLIT_SERVER_ADDRESS` | `0.0.0.0` | Streamlit (export into shell env) |

**Note:** Streamlit reads `STREAMLIT_SERVER_PORT` / `STREAMLIT_SERVER_ADDRESS`
from the *process* environment before Python even starts, so `load_dotenv()`
inside `app.py` runs too late to affect them. If you want those to take
effect, export the `.env` file into your shell first, e.g.:

```bash
export $(grep -v '^#' .env | xargs)
streamlit run frontend/app.py
```

Otherwise Streamlit just uses its own defaults (port 8501, `localhost`).

---

## 🔐 Security Notes

- `database/setup_users.py` stores the admin password as a bcrypt hash
  (see `shared/auth.py`), and `frontend/app.py` verifies logins against
  that hash — passwords are never stored in plaintext in the database.
- Still change `ADMIN_PASSWORD` in `.env` to a real password before
  deploying anywhere beyond local testing — the shipped default
  (`admin123`) is just a placeholder, and whoever can read your `.env`
  file can see it in plaintext even though the *database* no longer
  stores it that way.

---

## 🔮 Future Improvements

- Role-based access control
- MQTT authentication
- REST API integration
- Docker support
- Cloud database integration
- Dashboard analytics
- Push notifications

---

## Project Background

Developed as an internship project at the Airports Authority of India
(AAI), Netaji Subhas Chandra Bose International Airport, Kolkata.

---

## 📄 License

This project is intended for educational and internship purposes.