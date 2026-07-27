"""
Reset a staff/admin user's password.

setup_users.py uses INSERT OR IGNORE, so rerunning it after changing
ADMIN_PASSWORD in .env will NOT update an existing user's password —
the old (forgotten) hash stays in place. Use this script instead.

This does NOT require knowing the old password — only file/shell access
to run this script — since it's just a normal UPDATE against trolley.db.
"""
import sqlite3
import sys
import os
import getpass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.config import DB_NAME
from shared.auth import hash_password


def reset_password(username: str, new_password: str) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    if cursor.fetchone() is None:
        conn.close()
        return False

    cursor.execute(
        "UPDATE users SET password = ? WHERE username = ?",
        (hash_password(new_password), username),
    )
    conn.commit()
    conn.close()
    return True


if __name__ == "__main__":
    username = input("Username to reset: ").strip()
    new_password = getpass.getpass("New password: ")
    confirm = getpass.getpass("Confirm new password: ")

    if new_password != confirm:
        print("Passwords do not match. Aborting.")
        sys.exit(1)

    if reset_password(username, new_password):
        print(f"Password for '{username}' has been reset.")
    else:
        print(f"No user found with username '{username}'.")
