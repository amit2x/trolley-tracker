# Airport Trolley Tracker

Tracks trolley locations via MQTT/BLE beacons, stores pings in SQLite, and
serves a Streamlit dashboard for staff and passengers.

## Project structure

```
trolley_tracker/
├── .env                  # your local config (never commit this)
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

## Setup

```bash
pip install -r requirements.txt
```

The `.env` file holds every configurable value (DB filename, MQTT broker
info, default admin login, Streamlit port). Edit it to fit your environment
— nothing else needs to change. `.gitignore` already excludes `.env` and
`*.db` so secrets and local data never get committed.

## First-time setup (run once, from the project root)

```bash
python database/database.py       # creates trolley_tracking table + one sample row
python database/setup_users.py    # creates users/passengers tables + seeds admin login (password hashed with bcrypt)
```

> **Already ran the old flat-layout `setup_users.py` before this update?**
> Your `users` table has a plaintext password in it from before hashing was
> added. Delete `trolley.db` and re-run the two commands above so the admin
> row gets recreated with a proper bcrypt hash. Old plaintext rows will
> simply fail to log in after this change (by design) rather than silently
> working.

## Running the system

```bash
python backend/backend.py         # MQTT listener that writes pings into the DB
streamlit run frontend/app.py     # dashboard (staff + passenger login)
```

## Utility / debug scripts

| Script | Purpose |
|---|---|
| `database/current_status.py` | Prints latest known status per trolley |
| `database/history_view.py` | Prints last 1000 tracking records |
| `database/clear_old_data.py` | Wipes the `trolley_tracking` table |
| `database/test.py` | Prints the `trolley_tracking` table schema |

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

**Note:** Streamlit reads `STREAMLIT_SERVER_PORT`/`STREAMLIT_SERVER_ADDRESS`
from the *process* environment before Python even starts, so `load_dotenv()`
inside `app.py` runs too late to affect them. If you want those to take
effect, export the `.env` file into your shell first, e.g.:

```bash
export $(grep -v '^#' .env | xargs)
streamlit run frontend/app.py
```

Otherwise Streamlit just uses its own defaults (port 8501, localhost).

## Security notes

- `database/setup_users.py` stores the admin password as a bcrypt hash (see
  `shared/auth.py`), and `frontend/app.py` verifies logins against that hash
  — passwords are never stored in plaintext in the database.
- Still change `ADMIN_PASSWORD` in `.env` to a real password before
  deploying anywhere beyond local testing — the shipped default
  (`admin123`) is just a placeholder, and whoever can read your `.env` file
  can see it in plaintext even though the *database* no longer stores it
  that way.
