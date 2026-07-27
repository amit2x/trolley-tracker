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

- [🚀 What Is This Project?](#-what-is-this-project)
- [🏗️ The Big Picture — How Everything Connects](#️-the-big-picture--how-everything-connects)
- [📋 Prerequisites](#-prerequisites--what-you-need-before-you-start)
- [📦 Libraries Used — What and Why](#-libraries-used--what-and-why)
- [⚙️ Prerequisite Setup](#️-prerequisite-setup--getting-your-machine-ready)
- [▶️ Quick Start](#️-quick-start--running-the-prototype)
- [📁 What Each File Actually Does](#-what-each-file-actually-does)
- [🔗 How Every File Connects to Every Other File](#-how-every-file-connects-to-every-other-file)
- [🔧 Flashing the ESP32 Firmware](#-flashing-the-esp32-firmware)
- [🔄 The Order Things Run In](#-the-order-things-run-in-execution-hierarchy)
- [📡 How a Single Trolley Ping Flows Through the Whole System](#-how-a-single-trolley-ping-flows-through-the-whole-system)
- [🛰️ Simulating a Trolley Without Real Hardware](#️-simulating-a-trolley-without-real-hardware)
- [📶 RSSI → Status Logic](#-rssi--status-logic)
- [🗄️ Database Schema](#️-database-schema--whats-actually-stored)
- [📂 Project Folder Structure](#-project-folder-structure)
- [⚙️ Configuration Reference](#️-configuration-reference)
- [🛡️ Security Notes](#️-security-notes)
- [🛠️ Troubleshooting](#️-troubleshooting-common-first-run-issues)
- [🚀 Future Improvements](#-future-improvements)
- [📖 Project Background](#-project-background)
- [📄 License](#-license)

---


# 🚀 What Is This Project?

Imagine an airport where hundreds of luggage trolleys are scattered
across different terminals. Staff don't know where they are. Passengers
can't find one nearby. This project solves that problem.

Small BLE (Bluetooth Low Energy) beacons are attached to trolleys. As a
trolley moves around, nearby trolley-mounted scanners detect the nearest zone beacon, and report its
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
   [ESP32/beacon/beacon.ino — BLE Beacon mounted in an airport zone]
                │
                │  (advertises its name over BLE, e.g. "ZONE_A_BEACON")
                ▼
   [ESP32/trolley/trolley.ino — BLE Scanner + WiFi/MQTT client]
                │
                │  (scans for known beacon names, keeps the strongest
                │   RSSI match as the current zone, connects to WiFi)
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
the scripts in `database/`, and the firmware in `ESP32/`) exists to
**support** this chain — they set things up, maintain the database,
handle logins securely, or run on the physical hardware itself. None of
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
| **Arduino IDE or PlatformIO** | Only needed if you're flashing real ESP32 hardware, not just testing the software | [arduino.cc/en/software](https://www.arduino.cc/en/software) |
| **ESP32 boards (2+)** | One acts as a beacon (`ESP32/beacon/beacon.ino`), one or more act as trolley scanners (`ESP32/trolley/trolley.ino`) | Only needed for real hardware |
| **Arduino libraries: `NimBLE-Arduino`, `PubSubClient`, `ArduinoJson`** | Required by `trolley.ino` (BLE scanning, MQTT publishing, JSON payloads) and `beacon.ino` (BLE advertising) | Install via Library Manager in Arduino IDE, or `platformio.ini` if using PlatformIO |

You do **not** need to own real ESP32 hardware to explore this project —
you can simulate trolley pings by publishing fake MQTT messages
yourself (shown further down), so the backend and dashboard both work
without any physical device. The firmware in `ESP32/` is only needed if
you want to test with real beacons and scanners.

---

# 📦 Libraries Used — What and Why

Before setting things up, it helps to know exactly *what* gets installed
and *why* — both on the Python side and the firmware side — and which
specific parts of each library this project actually calls. This is
useful if something breaks and you need to know where to look in that
library's own documentation.

## Python Libraries

| Library | Why it's used | Specific components used in this project |
|---|---|---|
| **streamlit** | Turns plain Python into a web dashboard with almost no HTML/CSS/JS required — this is what renders `frontend/app.py` as something you open in a browser | `st.set_page_config()`, `st.session_state`, `st.title()`, `st.columns()`, `st.text_input()`, `st.button()`, `st.selectbox()`, `st.metric()`, `st.dataframe()`, `st.error()`, `st.warning()`, `st.info()`, `st.rerun()`, `st.toggle()`, `st.caption()` |
| **streamlit-autorefresh** | Adds a non-blocking way to make the dashboard refresh itself on a timer, without freezing the whole app the way a plain `time.sleep()` would | `st_autorefresh(interval=..., key=...)` |
| **pandas** | Handles the trolley data as a table (DataFrame) so it can be filtered by zone, have its `status` recalculated, and be displayed neatly in Streamlit | `pd.read_sql()` (runs a SQL query directly into a DataFrame), `.apply()`, `.unique()`, `.tolist()`, boolean filtering (`df[df.zone == z]`), `pd.to_datetime()` |
| **paho-mqtt** | The actual MQTT client library — lets `backend.py` connect to the Mosquitto broker, subscribe to the trolley topic, and react whenever a new ping arrives | `mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)`, `.on_connect`, `.on_message`, `.connect()`, `.subscribe()`, `.loop_forever()` |
| **schedule** | A simple way to say "run this function every 60 seconds" without writing your own timer/loop logic from scratch | `schedule.every(60).seconds.do(check_offline)`, `schedule.run_pending()` |
| **python-dotenv** | Reads the `.env` file and loads its key-value pairs into the environment, so `shared/config.py` can read them with `os.getenv()` — this is what lets you change settings without touching code | `load_dotenv()` |
| **bcrypt** | Password hashing — turns a plaintext password into a secure, salted hash before it's stored, and safely checks a login attempt against that hash later | `bcrypt.hashpw()`, `bcrypt.gensalt()`, `bcrypt.checkpw()` |
| **sqlite3** *(built into Python — not in `requirements.txt`)* | The actual database engine every script talks to. No separate database server is needed; the whole database is just one file (`trolley.db`) | `sqlite3.connect()`, `.cursor()`, `.execute()`, `.fetchone()`, `.fetchall()`, `.commit()`, `.close()`, `.row_factory = sqlite3.Row` |

### Standard library modules used (also built into Python, not installed via pip)

| Module | Why it's used | Specific components used |
|---|---|---|
| `json` | Converts the raw MQTT message payload (bytes/text) into a Python dictionary | `json.loads()` |
| `datetime` | Timestamps every ping when it's inserted, and calculates how long ago a trolley was last seen (for the OFFLINE check) | `datetime.now()`, `.strftime()`, `.strptime()`, `timedelta` |
| `time` | A short pause inside the scheduler's background loop, so it doesn't spin the CPU checking for pending jobs constantly | `time.sleep(1)` |
| `threading` | Runs the 60-second offline-check scheduler in the background *while* the main MQTT listener keeps running in the foreground at the same time | `threading.Thread(target=..., daemon=True)`, `.start()` |
| `sys` | Used only to modify Python's module search path, so every script can find and import the `shared/` package regardless of which folder it's run from | `sys.path.insert()` |
| `os` | Builds absolute file paths (so `shared/config.py` always finds the same `trolley.db` no matter where a script is launched from) and reads environment variables | `os.path.abspath()`, `os.path.dirname()`, `os.path.join()`, `os.path.isabs()`, `os.getenv()` |

## Firmware Libraries (ESP32 / Arduino, C++)

| Library | Why it's used | Specific components used |
|---|---|---|
| **NimBLE-Arduino** (`NimBLEDevice.h`) | A lightweight BLE (Bluetooth Low Energy) stack for the ESP32 — used by `beacon.ino` to broadcast a name, and by `trolley.ino` to scan for nearby beacons | `NimBLEDevice::init()`, `NimBLEDevice::getAdvertising()`, `NimBLEAdvertisementData`, `.setName()`, `.setFlags()`, `.setAdvertisementData()`, `.setScanResponseData()`, `NimBLEDevice::getScan()`, `.setActiveScan()`, `.setInterval()`, `.setWindow()`, `.getResults()`, `NimBLEAdvertisedDevice`, `.getName()`, `.getRSSI()` |
| **WiFi** (`WiFi.h`, built into the ESP32 Arduino core) | Connects the trolley scanner to your local WiFi network so it can reach the MQTT broker | `WiFi.begin()`, `WiFi.status()`, `WiFi.localIP()`, `WiFi.gatewayIP()` |
| **PubSubClient** | An MQTT client for microcontrollers — the ESP32 equivalent of `paho-mqtt` on the Python side | `PubSubClient mqttClient(espClient)`, `.setServer()`, `.connect()`, `.connected()`, `.publish()`, `.loop()`, `.state()` |
| **ArduinoJson** | Builds the small JSON payload (`{"trolley_id": ..., "zone": ..., "rssi": ...}`) that gets published over MQTT | `StaticJsonDocument<200>`, `serializeJson()` |
| **Arduino core** (`Arduino.h`) | The base framework every ESP32 sketch runs on — provides `Serial`, `delay()`, and the `setup()`/`loop()` structure itself | `Serial.begin()`, `Serial.print()` / `Serial.println()`, `delay()` |

**Why the built-in vs. installed distinction matters:** `sqlite3`,
`json`, `datetime`, `time`, `threading`, `sys`, and `os` all ship with
Python itself — you'll never see them in `requirements.txt`, and
`pip install -r requirements.txt` won't touch them. Only the six
third-party packages in the first table need to actually be installed.
Similarly, on the firmware side, `Arduino.h` comes bundled with the
ESP32 board package itself, while `NimBLE-Arduino`, `PubSubClient`, and
`ArduinoJson` need to be installed separately via the Arduino IDE's
Library Manager (or listed in `platformio.ini` if using PlatformIO).

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
listed there — Streamlit (the dashboard framework), streamlit-autorefresh
(the non-blocking auto-refresh timer used by the dashboard), pandas (for
handling tabular data), paho-mqtt (to talk MQTT), schedule (for
periodic background tasks), python-dotenv (to read the `.env` file),
and bcrypt (for password hashing).

### 2. Set up your configuration file

Copy `.env.example` to a new file named `.env`:

```bash
cp .env.example .env      # macOS/Linux
copy .env.example .env    # Windows
```

Open the new `.env` file in your editor. Since it's copied straight
from `.env.example` — the only version of this file that's actually
committed to the repo — it looks like this:

```env
DB_NAME=trolley.db
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_TOPIC=airport/trolleys
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-me
ADMIN_ROLE=admin
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

Replace `ADMIN_PASSWORD=change-me` with a real password of your choice
before running `setup_users.py` — whatever you set here becomes your
staff login password (bcrypt-hashed before it's stored, but the
plaintext still lives in your local `.env`, so keep that file private
either way). `.env` is
intentionally excluded from Git (via `.gitignore`) so your personal
settings and secrets never get committed — `.env.example` is the
template that *does* get committed, with harmless placeholder values.

### 3. Working with the MQTT Broker

**Start the broker:**

Start the Mosquitto MQTT broker on the machine that will run
`backend.py`.

Windows Command Prompt (Run as administrator):

```powershell
net start mosquitto
```

`net start` only works from an **elevated** Command Prompt or
PowerShell — right-click it in the Start Menu and choose "Run as
administrator," otherwise this fails with `System error 5 has
occurred. Access is denied.`

Alternatively, Mosquitto may be started manually from its installation
directory (no administrator rights needed for this route):

```bash
mosquitto
```

**Check the status (whether running or not):**

To check whether the Mosquitto broker is running, run:

Windows Command Prompt (Run as administrator):

```powershell
sc query mosquitto
```

Check the `STATE` field in the output — `STATE : 4 RUNNING` means the
broker is running.

**Stop the broker:**

To stop the broker, run:

Windows Command Prompt (Run as administrator):

```powershell
net stop mosquitto
```

---

### 4. Custom Configuration for Trolley Tracking

Add the following to the end of your `mosquitto.conf` file to configure
Mosquitto to accept ESP32 MQTT connections on port 1883, then save the
file. Open the file with administrator privileges before saving the
changes.

```mosquitto.conf
listener 1883 0.0.0.0
allow_anonymous true
```

---

# ▶️ Quick Start — Running the Prototype

Once the prerequisite setup above is done, here's the shortest path to
a working system — the same six-step sequence the original prototype
was run and demoed with, generalized so it works for anyone's clone of
this repo rather than any one person's local setup.

**Step 1: Prepare the ESP32 Devices** *(skip if you're only testing
with simulated pings — see [Simulating a Trolley Without Real
Hardware](#️-simulating-a-trolley-without-real-hardware))*
- Upload `ESP32/beacon/beacon.ino` to the ESP32 installed in the airport zone.
- Upload `ESP32/trolley/trolley.ino` to the ESP32 mounted on the trolley.
- Update the WiFi SSID, WiFi password, and MQTT broker IP address in
  your own `secrets.h` before uploading (copied from
  `secrets.h.example` — see [Flashing the ESP32
  Firmware](#-flashing-the-esp32-firmware)).
- Power both ESP32 devices using USB. (It's fine that the broker and
  backend aren't running yet — the trolley scanner simply retries its
  MQTT connection every 2 seconds until it can reach the broker, so
  powering it on early doesn't cause any errors.)

**Step 2: Start the MQTT Broker**

Start the Mosquitto MQTT broker on the backend computer.

Example (Windows Command Prompt):
```powershell
net start mosquitto
```
`net start` requires an **elevated** Command Prompt — right-click it in
the Start Menu and choose "Run as administrator" first, or this fails
with `Access is denied`.

Alternatively, Mosquitto may be started manually from its installation
directory (no administrator rights needed):
```bash
mosquitto
```

**Step 3: Initialise the Database** *(First Run Only)*

Execute the required database setup scripts:
```bash
python database/database.py
python database/setup_users.py
```
(This step is only required during the initial setup.)

**Step 4: Start the Backend Service**

Run the backend service:
```bash
python backend/backend.py
```
The backend subscribes to MQTT messages, processes incoming trolley
data, updates the SQLite database, and performs periodic offline
detection. Leave it running.

**Step 5: Launch the Dashboard**

Start the Streamlit application:
```bash
streamlit run frontend/app.py
```

**Step 6: Access the Dashboard**

Open a web browser and navigate to:
```
http://localhost:8501
```
Log in with the staff account you created via your own
`ADMIN_USERNAME`/`ADMIN_PASSWORD` in `.env`, or as a passenger using a
username + PNR from your own `passengers` table (either the one sample
row `setup_users.py` seeds, or one you've added yourself with
`add_passenger.py`).

---

# 📁 What Each File Actually Does

The project is organized into five folders, each with one clear job.
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

## 📁 `ESP32/` — the firmware that runs on the physical hardware

Two separate sketches, each meant for a different physical device. They
never run on the same board at the same time.

**`ESP32/beacon/beacon.ino`**
Flashed onto the ESP32 installed in an airport zone. It does
almost nothing except constantly advertise its own name (e.g.
`ZONE_A_BEACON`) over BLE — that name is how a scanner later identifies
which zone a trolley is near. Change `BEACON_NAME` at the top of the
file for each physical beacon you flash, then re-upload.

**`ESP32/trolley/trolley.ino`**
Flashed onto the ESP32 that acts as a zone scanner, mounted on the
trolley itself. On every loop it:
1. Connects to WiFi and to the Mosquitto broker (reconnecting
   automatically if either drops).
2. Runs a 5-second BLE scan and compares every device name it sees
   against the hardcoded `knownBeacons[]` list.
3. Keeps whichever known beacon had the strongest RSSI as the current
   `bestZone` / `bestRSSI`.
4. Publishes `{"trolley_id": ..., "zone": ..., "rssi": ...}` as JSON to
   the same MQTT topic `backend.py` is subscribed to.
5. Waits 30 seconds, then repeats.

**`ESP32/trolley/secrets.h`** *(not committed — see `.gitignore`)*
Holds the real `WIFI_SSID`, `WIFI_PASS`, and `MQTT_BROKER` values for
your network, so nothing sensitive is hardcoded in `trolley.ino` itself.

**`ESP32/trolley/secrets.h.example`**
The committed template for the file above. Copy it to `secrets.h` and
fill in your real values before uploading `trolley.ino` — see
[Flashing the ESP32 Firmware](#-flashing-the-esp32-firmware) below.

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
| **`reset_password.py`** | Overwrites an existing user's password with a freshly bcrypt-hashed new one, via a real `UPDATE` (not `INSERT OR IGNORE`) | Any time a staff member forgets their password — `setup_users.py` alone can't fix this, since it silently skips existing usernames |
| **`add_user.py`** | Adds a brand-new staff/admin login to the `users` table, with a properly hashed password | Whenever you need to onboard an additional staff member beyond the single seeded admin |
| **`add_passenger.py`** | Adds a brand-new passenger record to the `passengers` table (username, PNR, name, flight details) | Whenever you need to register a real passenger beyond the single hardcoded sample one |

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
6. If a message can't be parsed as valid JSON, or is missing a required
   field, `on_message()` catches that error, prints a warning to the
   console, and moves on — a single bad or corrupted message won't
   crash the whole backend and stop data collection for every other
   trolley.

## 📁 `frontend/` — what people actually see and click on

**`app.py`**
A Streamlit web application — this is literally what opens in your
browser. It has two logical halves:
- **Login page** — separate forms for staff (username + password,
  checked via `verify_password()`) and passengers (username + PNR,
  a booking reference number).
- **Dashboards** — staff see every trolley with filters and live counts;
  passengers see only active trolleys in their own zone.
- **Auto-refresh** — both dashboards include an "Auto-refresh" toggle
  (default on) plus an interval selector (10 / 30 / 60 / 120 seconds),
  powered by the `streamlit-autorefresh` package. This runs a small
  client-side timer that reruns the page on schedule *without* freezing
  the app — unlike a naive `time.sleep(60)` loop, you can still click
  "Refresh," change the zone filter, or log out at any moment, even
  mid-countdown. Turn it off if you'd rather refresh manually.

It never talks to MQTT or the beacons directly — its only source of
truth is the same database file that `backend.py` writes into.

---

# 🔗 How Every File Connects to Every Other File

The sections above explain what each file *does* on its own. This
section explains how they *depend on* each other — who imports whom,
who reads/writes the same database, and who talks to whom over the
network.

## Import graph — Python side

```text
shared/config.py
   │
   │  (imported by every script below — reads .env once, exposes
   │   DB_NAME, MQTT_BROKER, MQTT_PORT, MQTT_TOPIC, ADMIN_*, etc.)
   │
   ├──► backend/backend.py
   ├──► frontend/app.py
   ├──► database/database.py
   ├──► database/clear_old_data.py
   ├──► database/current_status.py
   ├──► database/history_view.py
   ├──► database/setup_users.py
   ├──► database/test.py
   ├──► database/reset_password.py
   ├──► database/add_user.py
   └──► database/add_passenger.py

shared/auth.py
   │
   │  (imported only where passwords are hashed or checked)
   │
   ├──► frontend/app.py               (verify_password, during staff login)
   ├──► database/setup_users.py       (hash_password, when seeding the admin)
   ├──► database/reset_password.py    (hash_password, when overwriting a password)
   └──► database/add_user.py          (hash_password, when adding a new staff login)

shared/__init__.py
   │
   └──► (not imported directly by name — its only job is to make Python
        treat the shared/ folder as a package at all, which is what
        makes "from shared.config import ..." possible in the first place)
```

**Every single one of those eleven scripts** (`backend.py`, `app.py`, and
all nine `database/*.py` files) starts with the identical two lines:

```python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.config import DB_NAME, ...
```

That first line is what makes the second line possible — without it,
Python wouldn't know to look one folder up from wherever the script
lives (`backend/`, `frontend/`, or `database/`) to find `shared/` sitting
next to those folders at the project root.

Nothing in `database/`, `backend/`, or `frontend/` ever imports *another
file from a different one of those three folders* — e.g. `app.py` never
imports anything from `backend.py`, and `current_status.py` never
imports anything from `database.py`. **`shared/` is the only thing that
connects them** — everything else is connected indirectly, through the
database file itself.

## The real connective tissue: `trolley.db`

Since none of the folders import each other directly, the database file
is what actually links everything together — it's a shared piece of
state that different, otherwise-unrelated scripts all read from or
write to independently, at different times:

```text
                         ┌─────────────────┐
                         │   trolley.db     │
                         │  (SQLite file)   │
                         └─────────────────┘
                                  ▲  ▲
                    writes to it  │  │  writes to it
                                  │  │
        backend/backend.py ──────┘  └────── database/setup_users.py
        (trolley_tracking table,           (users + passengers tables,
         every MQTT ping + every            once, during setup)
         60s offline check)

                                  ▲
                          also writes to it
                                  │
                       database/database.py
                    (creates trolley_tracking table
                     + inserts one sample row, once)

                                  ▲
                    updates/adds rows in users or passengers
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                          │
database/reset_password.py  database/add_user.py    database/add_passenger.py
(overwrites an existing      (adds a new staff        (adds a new passenger
 user's password hash)        login)                    record)

                                  ▲
                            reads from it
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                          │
frontend/app.py         database/current_status.py   database/history_view.py
(staff + passenger       (prints latest status         (prints last 1000
 dashboards)              per trolley to terminal)       tracking rows)

                                  ▲
                            deletes from it
                                  │
                       database/clear_old_data.py
                    (wipes trolley_tracking only)

                                  ▲
                          inspects its structure
                                  │
                            database/test.py
                       (prints column schema only)
```

This is why the **order things run in** matters so much (see that
section below) — `setup_users.py` will fail if `database.py` hasn't
created the database file yet, and `app.py`/`current_status.py` will
just show empty results (not an error) if `backend.py` has never
written anything.

## The network connections — how the firmware and backend talk

Beyond file imports and the shared database, two more connections tie
the physical hardware into this same system, over the network rather
than through Python imports:

```text
ESP32/beacon/beacon.ino
        │
        │  advertises its name over Bluetooth Low Energy
        │  (e.g. "ZONE_A_BEACON") — no WiFi, no MQTT, just BLE
        ▼
ESP32/trolley/trolley.ino
        │
        │  scans for that BLE name, picks the strongest RSSI match,
        │  then connects over WiFi to the Mosquitto broker and
        │  PUBLISHES a JSON message to the "airport/trolleys" topic
        ▼
   Mosquitto MQTT Broker            (a separate program, not part of
        │                            this repo — just installed and run)
        │  the broker forwards that same message to anyone SUBSCRIBED
        │  to "airport/trolleys"
        ▼
backend/backend.py
        │
        │  is the one and only subscriber — its on_message() function
        │  fires every time a message arrives, and THAT'S where the
        │  network connection turns back into a database write
        ▼
   trolley_tracking table in trolley.db
```

So `trolley.ino` and `backend.py` never import each other or know
anything about each other's code — they're connected purely by both
independently agreeing on the same **MQTT topic name**
(`airport/trolleys`, matching `MQTT_TOPIC` in `.env` on the Python side
and the `MQTT_TOPIC` constant hardcoded in the `.ino` file) and the same
**JSON field names** (`trolley_id`, `zone`, `rssi`). If either side
changes the topic name or a field name without updating the other, the
connection silently breaks — no error is thrown anywhere, messages just
stop being understood correctly.

`ESP32/beacon/beacon.ino` and `ESP32/trolley/trolley.ino` are similarly
connected only by convention, not by any shared file or import: the
`BEACON_NAME` you set in `beacon.ino` must exactly match one of the
entries in the `knownBeacons[]` array inside `trolley.ino` — there's no
code enforcing this at compile time or runtime, it's purely a manual
agreement between the two files.

## Full connection summary, one file at a time

| File | Imports from | Read/written by others via | Talks to over the network |
|---|---|---|---|
| `shared/config.py` | `python-dotenv`, `os` | Imported by all 11 Python scripts below | — |
| `shared/auth.py` | `bcrypt` | Imported by `app.py`, `setup_users.py`, `reset_password.py`, `add_user.py` | — |
| `database/database.py` | `shared.config` | Creates `trolley_tracking`, which every other DB-reading script depends on existing | — |
| `database/setup_users.py` | `shared.config`, `shared.auth` | Creates `users`/`passengers`, which `app.py`'s login depends on existing | — |
| `database/clear_old_data.py` | `shared.config` | Deletes rows that `backend.py` wrote and `app.py`/`current_status.py`/`history_view.py` would otherwise read | — |
| `database/current_status.py` | `shared.config` | Reads rows written by `backend.py` | — |
| `database/history_view.py` | `shared.config` | Reads rows written by `backend.py` | — |
| `database/test.py` | `shared.config` | Reads the schema created by `database.py` | — |
| `database/reset_password.py` | `shared.config`, `shared.auth` | Overwrites a row created by `setup_users.py` or `add_user.py`; read afterward by `app.py`'s login check | — |
| `database/add_user.py` | `shared.config`, `shared.auth` | Adds rows read afterward by `app.py`'s login check | — |
| `database/add_passenger.py` | `shared.config` | Adds rows read afterward by `app.py`'s passenger login check | — |
| `backend/backend.py` | `shared.config`, `paho-mqtt`, `schedule` | Writes the rows every other DB script reads | Subscribes to Mosquitto, topic `airport/trolleys` |
| `frontend/app.py` | `shared.config`, `shared.auth`, `streamlit-autorefresh` | Reads rows written by `backend.py`; reads login tables written by `setup_users.py`, `reset_password.py`, `add_user.py`, `add_passenger.py` | — (only touches the DB file, never MQTT directly) |
| `ESP32/beacon/beacon.ino` | (firmware libraries only, no shared code with Python) | — | Advertises over BLE, read by `trolley.ino`'s scanner |
| `ESP32/trolley/trolley.ino` | `ESP32/trolley/secrets.h` (its own WiFi/broker credentials) | — | Publishes to Mosquitto, topic `airport/trolleys`, read by `backend.py` |

---

# 🔧 Flashing the ESP32 Firmware

Skip this whole section if you're only testing with simulated pings
(see [Simulating a Trolley Without Real Hardware](#️-simulating-a-trolley-without-real-hardware)).

### 1. Set up `secrets.h` for the trolley scanner

```bash
cp ESP32/trolley/secrets.h.example ESP32/trolley/secrets.h
```

Open `ESP32/trolley/secrets.h` and fill in your real WiFi SSID/password
and the IP address of the machine running Mosquitto. Like `.env`,
`secrets.h` is git-ignored — only `secrets.h.example` is committed.

### 2. Flash the beacon(s)

Open `ESP32/beacon/beacon.ino` in the Arduino IDE, set `BEACON_NAME` to
match one of the zone names used in `knownBeacons[]` inside
`trolley.ino` (e.g. `ZONE_A_BEACON`), and upload it to the ESP32 installed in the airport zone. Repeat for each additional beacon/zone,
changing `BEACON_NAME` each time.

### 3. Flash the trolley scanner(s)

Open `ESP32/trolley/trolley.ino`, set a unique `TROLLEY_ID` for this
board (e.g. `T-001`), confirm `knownBeacons[]` lists every beacon name
you flashed in step 2, then upload it to the ESP32 mounted on the
trolley.

### 4. Power everything on in the right order

Mosquitto and `backend.py` should already be running (see the next
section) before you power on the trolley scanner — otherwise it will
just retry the MQTT connection every 2 seconds until the broker is
reachable. Beacons can be powered on at any time, since they only
advertise and don't depend on WiFi or MQTT.

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
        │
        ▼
  Power on beacon(s) and trolley scanner(s)   (optional — real hardware
                                                only; see "Flashing the
                                                ESP32 Firmware" if not
                                                already flashed)

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

1. A zone's BLE beacon broadcasts its identifier (e.g. `ZONE_A_BEACON`).
2. The ESP32 scanner mounted on trolley `T-003` detects that beacon,
   measures its signal strength (say, `-46`), and determines the
   current zone (say, `ZONE_A`).
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

> **Note:** the `id` column above is only accurate if `database.py`
> actually creates `trolley_tracking` with an
> `id INTEGER PRIMARY KEY AUTOINCREMENT` column. Double-check this
> against the real `database.py` before publishing — if there's no
> `id` column in the actual schema, remove that row from the table.

---

# 📂 Project Folder Structure

```text
trolley_tracker/
├── .env                  # your local settings (never committed)
├── .env.example          # template for .env (safe to commit)
├── .gitignore
├── requirements.txt
├── README.md
├── trolley.db            # the actual SQLite database file (never committed)
├── backend/
│   └── backend.py        # MQTT listener → writes pings into SQLite
├── database/
│   ├── database.py       # creates trolley_tracking table + sample row
│   ├── setup_users.py    # creates users/passengers tables + admin login
│   ├── clear_old_data.py # wipes trolley_tracking
│   ├── current_status.py # prints latest status per trolley
│   ├── history_view.py   # prints last 1000 tracking records
│   ├── test.py           # prints the trolley_tracking table schema
│   ├── reset_password.py # resets an existing user's password
│   ├── add_user.py       # adds a new staff/admin login
│   └── add_passenger.py  # adds a new passenger record
├── ESP32/
│   ├── beacon/
│   │   └── beacon.ino          # BLE beacon firmware (installed in airport zone)
│   └── trolley/
│       ├── secrets.h           # real WiFi/MQTT credentials (never committed)
│       ├── secrets.h.example   # template for secrets.h (safe to commit)
│       └── trolley.ino         # BLE scanner + WiFi/MQTT firmware
├── frontend/
│   └── app.py            # Streamlit dashboard (staff + passenger login)
└── shared/
    ├── config.py         # reads .env, exposes settings to every script
    ├── auth.py           # password hashing/verification helpers
    └── __init__.py
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
| `ADMIN_PASSWORD` | *(none — set your own; `.env.example` placeholder is `change-me`)* | `database/setup_users.py` |
| `ADMIN_ROLE` | `admin` | `database/setup_users.py` |
| `STREAMLIT_SERVER_PORT` | `8501` | Streamlit |
| `STREAMLIT_SERVER_ADDRESS` | `0.0.0.0` | Streamlit |

**Note on the Streamlit variables:** The default Streamlit settings
(`localhost:8501`) are suitable for most users. If you want the
dashboard to run on a different address or port, update the
`STREAMLIT_SERVER_ADDRESS` and `STREAMLIT_SERVER_PORT` values in your
`.env` file.

**Note on the ESP32 firmware:** `beacon.ino` and `trolley.ino` don't
read `.env` at all — they're separate C++ programs flashed directly
onto hardware. Their settings (`BEACON_NAME`, `TROLLEY_ID`,
`knownBeacons[]`, `MQTT_TOPIC`) are edited directly in the `.ino` files,
and WiFi/broker credentials live in `secrets.h` instead. If you change
`MQTT_TOPIC` in `.env`, update the matching `MQTT_TOPIC` constant in
`trolley.ino` too, or the backend and the firmware will be talking past
each other.

---

# 🛡️ Security Notes

- Staff passwords are hashed with bcrypt before storage — the database
  never contains a readable password.
- Bcrypt automatically applies a random "salt" to every password, so
  even two identical passwords produce two different-looking hashes in
  the database — this is normal and intentional, not a bug.

---

# 🛠️ Troubleshooting Common First-Run Issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'shared'` | Ran a script in a way that broke the path lookup, or `shared/__init__.py` is missing | Confirm you're running from inside the project, and that `shared/__init__.py` exists |
| `sqlite3.OperationalError: unable to open database file` | `DB_NAME` in `.env` points to a subfolder that doesn't exist yet | Either use a bare filename like `trolley.db`, or create that folder yourself first |
| Backend won't connect / hangs on startup | Mosquitto isn't running | Start it with `net start mosquitto` from an elevated Command Prompt, or run `mosquitto` manually from its install directory — see [Prerequisite Setup](#️-prerequisite-setup--getting-your-machine-ready) |
| Dashboard shows "No trolley data" | No pings have been received yet | Run the `mosquitto_pub` simulation command above, or connect real hardware |
| Login fails even with correct default password | `setup_users.py` was never run, or ran against an old database with plaintext passwords | Delete `trolley.db` and re-run `database.py` then `setup_users.py` |
| `trolley.ino` won't compile / missing `secrets.h` | You haven't copied the template yet | `cp ESP32/trolley/secrets.h.example ESP32/trolley/secrets.h` and fill in real values |
| Trolley scanner never leaves "Connecting to WiFi" | Wrong `WIFI_SSID`/`WIFI_PASS` in `secrets.h`, or ESP32 out of router range | Double-check `secrets.h`, move the board closer to the router |
| Scanner sees the beacon but zone stays `UNKNOWN` | `BEACON_NAME` on the beacon doesn't exactly match an entry in `trolley.ino`'s `knownBeacons[]` | Make sure the names match character-for-character (case-sensitive) |

---

# 🚀 Future Improvements

- Role-based access control — the `users` table already has a `role`
  column (e.g. `admin`, `staff`), and `add_user.py` lets you assign any
  role you like when creating a login, but `app.py` doesn't actually
  check it for anything yet. Right now, any logged-in user whose role
  isn't `"passenger"` gets routed to the exact same `admin_dashboard()`
  with identical full access — `role` is currently just a cosmetic label
  shown on screen (`Logged in as X (role)`), not an actual permission
  gate. A real implementation would branch on `role` in `app.py` to give
  `staff` a more limited view than `admin` — worth doing once more than
  one kind of staff login actually needs to exist, so newer or
  lower-trust staff aren't handed the same full access as an admin
- MQTT authentication (currently the broker accepts unauthenticated
  connections, fine for local testing, not for production) — anyone on
  the same network as the broker can currently publish fake trolley
  pings to `airport/trolleys` with no credentials at all, since
  `client.connect(MQTT_BROKER, MQTT_PORT)` in both `backend.py` and
  `trolley.ino` never sends a username/password. Adding broker-level
  auth would stop anyone but your own devices from writing to the topic
- REST API integration — right now the only ways to get trolley data
  out of this system are opening the Streamlit dashboard as a human, or
  querying `trolley.db` directly with SQL. There's no way for a mobile
  app, a kiosk display, or any other external service to programmatically
  ask "what's the status of T-001?" without duplicating the database
  access logic itself — a small REST layer (e.g. `GET /trolleys/current`)
  would let other tools consume this data without touching SQLite directly
- Docker support — right now, setting this up on a new machine means
  manually installing Python, Mosquitto, and every dependency in
  `requirements.txt` in the right order, plus getting environment
  variables and file paths right. Containerizing `backend.py`, `app.py`,
  and Mosquitto would make setup a single reproducible command instead
  of a multi-step manual process
- Cloud database integration — `trolley.db` is a single local file on
  one machine. If that machine goes down, is reformatted, or two people
  need to run the dashboard from different locations at once, there's
  currently no shared source of truth — everything lives and dies with
  that one file. A cloud-hosted database would let multiple backend
  instances and dashboard users share the same live data
- Dashboard analytics — `app.py` currently only shows live counts and a
  raw table (Total / Active / Weak / Offline metrics). There's no way to
  see trends over time — e.g. which zones run low on trolleys most
  often, or what time of day demand peaks — even though `trolley_tracking`
  already stores enough historical data to answer exactly those questions
- Push notifications — right now, noticing that a trolley has gone
  `OFFLINE` or that a zone has run out of `ACTIVE` trolleys requires
  someone to actively have the dashboard open and either wait for
  auto-refresh or click "Refresh" themselves. There's no way to be
  proactively alerted (e.g. via email, SMS, or a Slack message) when
  something needs attention
- Database encryption at rest (SQLCipher) — encrypting the database file itself would add protection against the raw
  file being copied or read outside the app, at the cost of managing an encryption key that must never be lost
- Automated database backups — a scheduled or on-demand script that
  copies `trolley.db` to a timestamped backup file, so a corrupted
  database or accidental `clear_old_data.py` run isn't unrecoverable

---

# 📖 Project Background

Developed as an internship project at the Airports Authority of India
(AAI), Netaji Subhas Chandra Bose International Airport, Kolkata.

---

# 📄 License

This project is intended for educational and internship purposes.
