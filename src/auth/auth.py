"""
Authentication logic: registration, login, session management.
Uses bcrypt for password hashing and st.session_state for session tracking.
"""
import bcrypt
import streamlit as st
from sqlalchemy import text

from src.db.connection import engine


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def register_user(username: str, email: str, password: str, name: str) -> tuple[bool, str]:
    """Returns (success, message)."""
    from sqlalchemy.exc import IntegrityError

    username = username.strip().lower()
    email = email.strip().lower()

    if not username or not email or not password or not name:
        return False, "All fields are required."
    if len(password) < 8:
        return False, "Password must be at least 8 characters."

    with engine.connect() as conn:
        existing = conn.execute(
            text("SELECT user_id FROM users WHERE username = :u OR email = :e"),
            {"u": username, "e": email},
        ).fetchone()
        if existing:
            return False, "Username or email already registered."

        password_hash = hash_password(password)
        try:
            conn.execute(
                text(
                    "INSERT INTO users (username, email, password_hash, name) "
                    "VALUES (:u, :e, :p, :n)"
                ),
                {"u": username, "e": email, "p": password_hash, "n": name},
            )
            conn.commit()
        except IntegrityError:
            conn.rollback()
            return False, "Username or email already registered."

    return True, "Account created. You can now log in."

def authenticate_user(username: str, password: str) -> tuple[bool, str, dict | None]:
    """Returns (success, message, user_dict or None)."""
    username = username.strip().lower()

    with engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT user_id, username, email, password_hash, name "
                "FROM users WHERE username = :u"
            ),
            {"u": username},
        ).fetchone()

    if row is None:
        return False, "Invalid username or password.", None

    user_id, db_username, email, password_hash, name = row

    if not verify_password(password, password_hash):
        return False, "Invalid username or password.", None

    user_dict = {"user_id": user_id, "username": db_username, "email": email, "name": name}
    return True, "Login successful.", user_dict


def login_user(user_dict: dict) -> None:
    st.session_state["authenticated"] = True
    st.session_state["user_id"] = user_dict["user_id"]
    st.session_state["username"] = user_dict["username"]
    st.session_state["name"] = user_dict["name"]


def logout_user() -> None:
    for key in ("authenticated", "user_id", "username", "name"):
        st.session_state.pop(key, None)


def is_authenticated() -> bool:
    return st.session_state.get("authenticated", False)


def require_auth() -> None:
    """Call at the top of every protected page. Stops execution if not logged in."""
    if not is_authenticated():
        st.warning("Please log in to access this page.")
        st.stop()