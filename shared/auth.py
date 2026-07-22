"""
Password hashing helpers used by setup_users.py (to store hashes) and
app.py (to verify a login attempt against a stored hash).

Uses bcrypt, which automatically generates and embeds a random salt per
password, so two identical passwords produce different hashes and cannot
be matched with a plain SQL `WHERE password = ?` — always fetch the stored
hash by username first, then call verify_password().
"""
import bcrypt


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password for storage. Returns a str safe for a TEXT column."""
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Check a login attempt's plaintext password against a stored bcrypt hash."""
    if not stored_hash:
        return False
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), stored_hash.encode("utf-8"))
    except ValueError:
        # stored_hash isn't a valid bcrypt hash (e.g. leftover plaintext
        # from before this change was made) — treat as no match.
        return False
