import re
import bcrypt
from datetime import datetime
from app.database import fetch_one, execute_insert, execute_query

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, pwd_hash: str) -> bool:
    """Verify password against bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), pwd_hash.encode("utf-8"))
    except Exception:
        return False

def validate_credentials(username: str, password: str) -> str | None:
    """Validate username and password formats according to application rules."""
    if not username or len(username) < 5:
        return "Username must be at least 5 characters long."
    if not re.search(r"[A-Z]", username) or not re.search(r"[a-z]", username):
        return "Username must contain both uppercase and lowercase letters."

    if not password or len(password) < 5:
        return "Password must be at least 5 characters long."
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return "Password must contain both letters and numbers."
    if not re.search(r"[$%*@#&!]", password):
        return "Password must contain at least one special character ($, %, *, @, #, !, &)."

    return None

def find_user_by_username(username: str):
    """Retrieve user record by username."""
    return fetch_one("SELECT user_id, uname, pwd_hash, role, created_at FROM users WHERE uname = %s", (username,))

def find_user_by_id(user_id: int):
    """Retrieve user record by user ID."""
    return fetch_one("SELECT user_id, uname, pwd_hash, role, created_at FROM users WHERE user_id = %s", (user_id,))

def register_user(username: str, password: str, role: str = "player") -> tuple[bool, str]:
    """Register a new user in the database."""
    validation_err = validate_credentials(username, password)
    if validation_err:
        return False, validation_err

    existing = find_user_by_username(username)
    if existing:
        return False, "Username already exists"

    db_role = role.strip().lower() if role else "player"
    if db_role == "user":
        db_role = "player"
    if db_role not in ("admin", "player"):
        return False, "Invalid role specified."

    pwd_hash = hash_password(password)
    created_at = datetime.now()

    query = """
        INSERT INTO users (uname, pwd_hash, role, created_at)
        VALUES (%s, %s, %s, %s)
        RETURNING user_id, uname, role, created_at
    """
    new_user = execute_insert(query, (username, pwd_hash, db_role, created_at))
    if new_user:
        return True, "Registration successful"
    return False, "Failed to register user"

def authenticate_user(username: str, password: str):
    """Authenticate user with username and password."""
    user = find_user_by_username(username)
    if not user:
        return None
    if verify_password(password, user["pwd_hash"]):
        return user
    return None

