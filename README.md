<div align="center">

# ✈️ Airport Trolley Tracker

**A complete beginner's guide to understanding, setting up, and running this project**

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![MQTT](https://img.shields.io/badge/MQTT-Mosquitto-green)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightblue)
![License](https://img.shields.io/badge/License-Educational-orange)

</div>

## 📚 Table of Contents

- 🚀 What Is This Project?
- 🏗️ The Big Picture — How Everything Connects
- 📋 Prerequisites
- ⚙️ Prerequisite Setup
- 📁 What Each File Actually Does
- 🔄 The Order Things Run In
- 📡 How a Single Trolley Ping Flows Through the Whole System
- 🛰️ Simulating a Trolley Without Real Hardware
- 📶 RSSI → Status Logic
- 🗄️ Database Schema
- 🔐 Default Credentials
- 📂 Project Folder Structure
- ⚙️ Configuration Reference
- 🛡️ Security Notes
- 🛠️ Troubleshooting
- 🚀 Future Improvements
- 📖 Project Background
- 📄 License

---


# 🚀 What Is This Project?

Imagine an airport where hundreds of luggage trolleys are scattered
across different terminals. Staff don't know where they are. Passengers
can't find one nearby. This project solves that problem.

Small BLE (Bluetooth Low Energy) beacons are attached to trolleys. As a
trolley moves around, nearby scanners pick up its signal and report its
approximate location (its "zone") and signal strength. That information
travels over MQTT (a lightweight messaging protocol built for exactly
this kind of device-to-server communication) to a Python program, which
saves it into a small database. A web dashboard then shows, in real
time, where every trolley is and whether it's currently usable.

Two kinds of people use the dashboard:
- **Staff**, who log in and see *all* trolleys across *all* zones.
- **Passengers**, who log in and see only the *available* trolleys in
  *their* zone.

---

# 🏗️ The Big Picture — How Everything Connects

Before touching any code, it helps to see the whole chain, start to
finish:

```text
   [ESP32 BLE Beacon on a trolley]
                │
                │  (broadcasts a signal)
                ▼
   [ESP32 BLE Scanner nearby]
                │
                │  (measures signal strength = RSSI, notes the zone)
                ▼
   [Mosquitto MQTT Broker]
                │
                │  (passes the message along, like a mail sorting office)
                ▼
   [backend/backend.py]  ◄── this is the first file of OUR code that runs
                │
                │  (reads the message, decides ACTIVE / WEAK / OFFLINE,
                │   and saves a row into the database)
                ▼
   [trolley.db  — the SQLite database file]
                │
                │  (just sits there, holding data, until someone asks for it)
                ▼
   [frontend/app.py]  ◄── the Streamlit dashboard staff & passengers open
                │
                ▼
   [Your browser — the actual dashboard you see and click around in]
```

Everything else in this project (`shared/config.py`, `shared/auth.py`,
the scripts in `database/`) exists to **support** this chain — they set
things up, maintain the database, or handle logins securely. None of
them are the "main" program by themselves; they're the scaffolding that
lets `backend.py` and `app.py` do their jobs correctly.

---

# 📋 Prerequisites — What You Need Before You Start

Think of these as the tools you must have on your workbench before you
can build anything.

| Requirement | Why you need it | How to get it |
|---|---|---|
| **Python 3.9+** | Every script in this project is Python | [python.org/downloads](https://www.python.org/downloads/) |
| **pip** | Installs Python packages | Comes bundled with Python |
| **Mosquitto MQTT broker** | The "mail sorting office" that passes beacon messages to `backend.py` | [mosquitto.org/download](https://mosquitto.org/download/) |
| **Git** | To clone/manage this repository | [git-scm.com](https://git-scm.com/) |
| **A code editor** (e.g. VS Code) | To view/edit the code comfortably | [code.visualstudio.com](https://code.visualstudio.com/) |
| **ESP32 boards + BLE beacon firmware** | Only needed if you're running real hardware, not just testing the software | Outside the scope of this README |

You do **not** need to own real ESP32 hardware to explore this project —
you can simulate trolley pings by publishing fake MQTT messages
yourself (shown further down), so the backend and dashboard both work
without any physical device.

---

# ⚙️ Prerequisite Setup — Getting Your Machine Ready

Do these once, in order, before running anything from this repo.

### 1. Install Python packages this project needs

From the project's root folder (the top-level folder containing
`README.md`, `.env`, `shared/`, etc.):

```bash
pip install -r requirements.txt
```

This single command reads `requirements.txt` and installs everything
listed there — Streamlit (the dashboard framework), pandas (for
handling tabular data), paho-mqtt (to talk MQTT), schedule (for
periodic background tasks), python-dotenv (to read the `.env` file),
and bcrypt (for password hashing).

### 2. Set up your configuration file

Copy `.env.example` to a new file named `.env`:

```bash
cp .env.example .env      # macOS/Linux
copy .env.example .env    # Windows
```

Open `.env` in your editor. It looks like this:

```env
DB_NAME=trolley.db
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_TOPIC=airport/trolleys
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_ROLE=admin
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

You can leave these as defaults for local testing. `.env` is
intentionally excluded from Git (via `.gitignore`) so your personal
settings and secrets never get committed — `.env.example` is the
template that *does* get committed, with harmless placeholder values.

### 3. Start the MQTT broker

```bash
mosquitto
```

Leave this running in its own terminal window. If it's not running,
`backend.py` will fail to connect later.

---

# 📁 What Each File Actually Does

The project is organized into four folders, each with one clear job.
Think of each folder as a department in a small company.

## 📁 `shared/` — the shared toolbox

Both the backend and the frontend depend on this folder. Nothing here
runs by itself — it only gets *imported* by other scripts.

**`shared/config.py`**
The single place that reads your `.env` file and turns it into ready-to-use
Python values (`DB_NAME`, `MQTT_BROKER`, `ADMIN_PASSWORD`, etc.). Every
other script imports settings from here instead of reading `.env`
directly — so if you ever change a setting, you only change it in one
place (`.env`), and every script picks it up automatically.

It also does one clever thing: it converts `DB_NAME` into a full,
absolute file path based on the project's root folder. That guarantees
every script — no matter which folder you run it from — always opens
the *exact same* database file, never a duplicate copy.

**`shared/auth.py`**
Handles password security using bcrypt. It has two functions:
- `hash_password()` — scrambles a plain password into an unreadable hash
  before it's stored, so even if someone reads the database file
  directly, they can't see anyone's real password.
- `verify_password()` — checks a login attempt against that stored hash,
  returning `True` or `False`.

**`shared/__init__.py`**
An empty file that simply tells Python "treat this folder as an
importable package." You'll never need to open or edit it.

## 📁 `database/` — one-off setup & maintenance tools

None of these run continuously — you run each one when you need it, and
it finishes and exits.

| File | What it does | When you'd run it |
|---|---|---|
| **`database.py`** | Creates the `trolley_tracking` table and inserts one sample row | Once, during first-time setup |
| **`setup_users.py`** | Creates the `users` and `passengers` tables, and seeds one admin login + one sample passenger | Once, right after `database.py` |
| **`current_status.py`** | Prints the *latest* known status of every trolley to your terminal | Any time you want a quick text-based check without opening the dashboard |
| **`history_view.py`** | Prints the last 1000 recorded pings | Debugging — seeing the raw history of what's been recorded |
| **`clear_old_data.py`** | Deletes every row from `trolley_tracking` (but keeps `users`/`passengers` intact) | When you want to reset tracking data during testing |
| **`test.py`** | Prints the database's column structure (schema) | Confirming the table looks the way you expect |

## 📁 `backend/` — the always-running data collector

**`backend.py`**
This is the only script meant to run *continuously*, in the background,
for as long as your system is "live." It:
1. Connects to the Mosquitto broker and subscribes to the trolley topic.
2. Every time a message arrives, it reads the trolley's ID, zone, and
   signal strength (RSSI).
3. Decides the trolley's status from that RSSI value.
4. Writes a new row into the database with that information.
5. Separately, once every 60 seconds, it checks the database for any
   trolley that hasn't reported in over 5 minutes, and marks it
   `OFFLINE`.

## 📁 `frontend/` — what people actually see and click on

**`app.py`**
A Streamlit web application — this is literally what opens in your
browser. It has two logical halves:
- **Login page** — separate forms for staff (username + password,
  checked via `verify_password()`) and passengers (username + PNR,
  a booking reference number).
- **Dashboards** — staff see every trolley with filters and live counts;
  passengers see only active trolleys in their own zone.

It never talks to MQTT or the beacons directly — its only source of
truth is the same database file that `backend.py` writes into.

---

# 🔄 The Order Things Run In (Execution Hierarchy)

Some scripts must run *before* others, or they'll fail. Here's the
correct order, from the very first time you touch this project onward:

```text
STEP 1  (one-time, in this exact order)
────────────────────────────────────────
  python database/database.py
        │
        └─► creates trolley.db + the trolley_tracking table

  python database/setup_users.py
        │
        └─► adds the users + passengers tables into that SAME trolley.db,
            and creates your admin login

STEP 2  (every time you want the system "live")
────────────────────────────────────────────────
  Start Mosquitto           (must be running FIRST)
        │
        ▼
  python backend/backend.py     (leave this running — it listens forever)
        │
        ▼
  streamlit run frontend/app.py (open this in your browser)

STEP 3  (any time, optional, for checking things)
───────────────────────────────────────────────────
  python database/current_status.py
  python database/history_view.py
  python database/test.py
  python database/clear_old_data.py
```

**Why this order matters:** `setup_users.py` and `backend.py` both
assume the database file already exists — `database.py` is what
originally creates it. Similarly, `app.py` only ever *reads* from the
database; if `backend.py` has never run and no beacons have reported in,
the dashboard will simply show "No trolley data" rather than error out.

---

# 📡 How a Single Trolley Ping Flows Through the Whole System

Walking through one real example ties everything together:

1. A trolley's BLE beacon broadcasts a signal.
2. A nearby ESP32 scanner picks it up, measures signal strength
   (say, `-46`), and notes the zone (say, `ZONE_A`).
3. The scanner publishes this JSON to the MQTT broker:
   ```json
   {"trolley_id": "T-003", "zone": "ZONE_A", "rssi": -46}
   ```
4. `backend/backend.py` — which has been sitting connected to the
   broker this whole time — receives that message instantly.
5. It runs the message through `determine_status()`:
   - RSSI of `-46` is greater than `-99` → status = `"ACTIVE"`.
6. It writes a new row into `trolley_tracking`:
   `T-003 | ZONE_A | -46 | ACTIVE | <current timestamp>`
7. A staff member or passenger, sitting on the Streamlit dashboard,
   clicks "Refresh." `app.py` re-runs its database query, sees this new
   row, and displays trolley `T-003` as available in `ZONE_A`.

That's the entire system, end-to-end — one beacon ping becomes one
database row becomes one line of information on someone's screen.

---

# 🛰️ Simulating a Trolley Without Real Hardware

If you don't have ESP32 hardware yet but want to see the system work,
you can fake a beacon ping using any MQTT publishing tool. For example,
using `mosquitto_pub` (comes bundled with Mosquitto):

```bash
mosquitto_pub -h localhost -t airport/trolleys -m "{\"trolley_id\":\"T-001\",\"zone\":\"ZONE_A\",\"rssi\":-40}"
```

As long as `backend.py` is running and connected, this message will be
picked up and inserted into the database exactly like a real beacon
ping would be.

---

# 📶 RSSI → Status Logic

RSSI (Received Signal Strength Indicator) is just a number describing
how strong a wireless signal is — closer to `0` means a stronger, closer
signal; more negative means weaker or farther away.

| Condition | Meaning | Status |
|---|---|---|
| RSSI = -999 | Special sentinel value meaning "beacon unreachable" | `OUT_OF_RANGE` |
| RSSI > -99 | Strong, nearby signal | `ACTIVE` |
| RSSI ≤ -99 | Signal detected, but weak/distant | `WEAK_SIGNAL` |
| No new ping in 5 minutes | Backend hasn't heard from this trolley in a while | `OFFLINE` |

---

# 🗄️ Database Schema — What's Actually Stored

## `trolley_tracking`
One row per ping ever received.

| Column | Type | Meaning |
|---|---|---|
| `id` | INTEGER (auto-numbered) | A unique number for this specific row/ping |
| `trolley_id` | TEXT | Which trolley sent this ping (e.g. `T-003`) |
| `zone` | TEXT | Which zone it was detected in |
| `rssi` | INTEGER | Signal strength at the time of the ping |
| `status` | TEXT | Computed status (`ACTIVE` / `WEAK_SIGNAL` / etc.) |
| `timestamp` | TEXT | When this ping was recorded |

## `users`
One row per staff login.

| Column | Type | Meaning |
|---|---|---|
| `username` | TEXT (primary key) | Staff login name |
| `password` | TEXT | Bcrypt **hash** of the password — never plaintext |
| `role` | TEXT | e.g. `admin` |

## `passengers`
One row per passenger allowed to log in.

| Column | Type | Meaning |
|---|---|---|
| `username` | TEXT (primary key) | Passenger login name |
| `pnr` | TEXT | Their booking reference, used as a second login factor |
| `name` | TEXT | Display name |
| `flight_number` | TEXT | Their flight |
| `scheduled_time` | TEXT | Their flight's scheduled time |
| `gate` | TEXT | Their departure gate |

---

# 🔐 Default Credentials (Local Testing Only)

**Staff login**
- Username: `admin`
- Password: `admin123` (or whatever you set as `ADMIN_PASSWORD` in `.env`)

**Passenger login**
- Username: `userid`
- PNR: `PNR12345`

⚠️ These are placeholders meant only for trying things out on your own
machine. Change `ADMIN_PASSWORD` in `.env` to something real before this
ever runs anywhere beyond local testing — and remember that even though
the *database* only stores a bcrypt hash, your `.env` file itself still
holds the plaintext password, so keep that file private.

---

# 📂 Project Folder Structure

```text
trolley_tracker/
├── .env                  # your local settings (never committed)
├── .env.example          # template for .env (safe to commit)
├── .gitignore
├── requirements.txt
├── README.md
├── shared/
│   ├── config.py         # reads .env, exposes settings to every script
│   ├── auth.py           # password hashing/verification helpers
│   └── __init__.py
├── backend/
│   └── backend.py        # MQTT listener → writes pings into SQLite
├── frontend/
│   └── app.py            # Streamlit dashboard (staff + passenger login)
└── database/
    ├── database.py       # creates trolley_tracking table + sample row
    ├── setup_users.py    # creates users/passengers tables + admin login
    ├── clear_old_data.py # wipes trolley_tracking
    ├── current_status.py # prints latest status per trolley
    ├── history_view.py   # prints last 1000 tracking records
    └── test.py           # prints the trolley_tracking table schema
```

**Why every script can import `shared/` no matter where it's run from:**
each script starts with a small block that calculates the project's root
folder from its own file location, then adds that root folder to
Python's search path. This means running a script from the project root,
from inside its own subfolder, or from anywhere else always resolves to
the exact same `shared/` folder and the exact same database file —
nothing breaks depending on which directory you happened to be standing
in when you typed the command.

---

# ⚙️ Configuration Reference

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

**Note on the Streamlit variables:** Streamlit reads its port/address
settings from your terminal's environment *before* Python even starts
running — so `.env` alone won't change them, since `load_dotenv()`
inside `app.py` runs too late. If you want to change them, export the
`.env` file into your shell first:

```bash
export $(grep -v '^#' .env | xargs)
streamlit run frontend/app.py
```

Otherwise, Streamlit just uses its own defaults (port `8501`, address
`localhost`).

---

# 🛡️ Security Notes

- Staff passwords are hashed with bcrypt before storage — the database
  never contains a readable password.
- Bcrypt automatically applies a random "salt" to every password, so
  even two identical passwords produce two different-looking hashes in
  the database — this is normal and intentional, not a bug.
- Your `.env` file is excluded from Git by `.gitignore`, so your real
  admin password and any local settings never get committed to the
  repository.
- If you previously ran an older version of this project that stored
  plaintext passwords, delete `trolley.db` and re-run `database.py` +
  `setup_users.py` so your admin account gets recreated properly hashed.

---

# 🛠️ Troubleshooting Common First-Run Issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'shared'` | Ran a script in a way that broke the path lookup, or `shared/__init__.py` is missing | Confirm you're running from inside the project, and that `shared/__init__.py` exists |
| `sqlite3.OperationalError: unable to open database file` | `DB_NAME` in `.env` points to a subfolder that doesn't exist yet | Either use a bare filename like `trolley.db`, or create that folder yourself first |
| Backend won't connect / hangs on startup | Mosquitto isn't running | Start `mosquitto` in its own terminal first |
| Dashboard shows "No trolley data" | No pings have been received yet | Run the `mosquitto_pub` simulation command above, or connect real hardware |
| Login fails even with correct default password | `setup_users.py` was never run, or ran against an old database with plaintext passwords | Delete `trolley.db` and re-run `database.py` then `setup_users.py` |

---

# 🚀 Future Improvements

- Role-based access control (multiple staff permission levels)
- MQTT authentication (currently the broker accepts unauthenticated
  connections, fine for local testing, not for production)
- REST API integration
- Docker support
- Cloud database integration
- Dashboard analytics
- Push notifications

---

# 📖 Project Background

Developed as an internship project at the Airports Authority of India
(AAI), Netaji Subhas Chandra Bose International Airport, Kolkata.

---

# 📄 License

This project is intended for educational and internship purposes.
