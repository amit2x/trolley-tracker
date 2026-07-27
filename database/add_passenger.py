"""
Add a new passenger to the passengers table.

setup_users.py only ever seeds ONE hardcoded sample passenger, once.
This script lets you register real passengers afterward, each with
their own username + PNR (used together as their login).
"""
import sqlite3
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.config import DB_NAME


def add_passenger(username, pnr, name, flight_number, scheduled_time, gate) -> bool:
    """
    Returns True if the passenger was newly added, False if that
    username already exists (usernames are the primary key, so each
    must be unique).
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM passengers WHERE username = ?", (username,))
    if cursor.fetchone() is not None:
        conn.close()
        return False

    cursor.execute("""
        INSERT INTO passengers
        (username, pnr, name, flight_number, scheduled_time, gate)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (username, pnr, name, flight_number, scheduled_time, gate))
    conn.commit()
    conn.close()
    return True


if __name__ == "__main__":
    username = input("Passenger username: ").strip()
    pnr = input("PNR (booking reference): ").strip()
    name = input("Full name: ").strip()
    flight_number = input("Flight number (e.g. AI-202): ").strip()
    scheduled_time = input("Scheduled time (YYYY-MM-DD HH:MM:SS): ").strip()
    gate = input("Gate (e.g. Gate 14): ").strip()

    if not username or not pnr:
        print("Username and PNR cannot be empty. Aborting.")
        sys.exit(1)

    if add_passenger(username, pnr, name, flight_number, scheduled_time, gate):
        print(f"Passenger '{username}' added.")
    else:
        print(f"A passenger with username '{username}' already exists.")
