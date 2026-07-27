"""
Add a new staff/admin user to the users table.

setup_users.py only ever seeds ONE hardcoded admin account, once. This
script lets you add any number of additional staff logins afterward,
with a properly bcrypt-hashed password — no plaintext ever touches the
database.

Run this any time you need to onboard a new staff member.
"""
import sqlite3
import sys
import os
import getpass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.config import DB_NAME
from shared.auth import hash_password


def add_user(username: str, password: str, role: str = "staff") -> bool:
    """
    Returns True if the user was newly added, False if that username
    already exists (in which case nothing was changed — use
    reset_password.py to update an existing user's password instead).
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    if cursor.fetchone() is not None:
        conn.close()
        return False

    cursor.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        (username, hash_password(password), role),
    )
    conn.commit()
    conn.close()
    return True


if __name__ == "__main__":
    username = input("New username: ").strip()
    role = input("Role (e.g. admin/staff) [staff]: ").strip() or "staff"
    password = getpass.getpass("Password: ")
    confirm = getpass.getpass("Confirm password: ")

    if password != confirm:
        print("Passwords do not match. Aborting.")
        sys.exit(1)

    if not username or not password:
        print("Username and password cannot be empty. Aborting.")
        sys.exit(1)

    if add_user(username, password, role):
        print(f"User '{username}' added with role '{role}'.")
    else:
        print(f"A user named '{username}' already exists. "
              f"Use reset_password.py if you meant to change their password.")
