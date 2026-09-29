import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

def get_db_connection():
    """Create and return a new database connection."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def fetch_one(query: str, params: tuple = None):
    """Execute a query and fetch a single record as a dict."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            result = cur.fetchone()
            return dict(result) if result else None
    finally:
        conn.close()

def fetch_all(query: str, params: tuple = None):
    """Execute a query and fetch all records as a list of dicts."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            results = cur.fetchall()
            return [dict(row) for row in results]
    finally:
        conn.close()

def execute_query(query: str, params: tuple = None):
    """Execute an INSERT/UPDATE/DELETE query and commit changes."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()
            return cur.rowcount
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def execute_insert(query: str, params: tuple = None):
    """Execute an INSERT query with RETURNING clause and return the created record or value."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            result = cur.fetchone()
            conn.commit()
            return dict(result) if result else None
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def verify_connection():
    """Verify database connection and test query execution."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM users;")
            user_count = cur.fetchone()[0]
            print(f"Database connection verified successfully! Total users in DB: {user_count}")
            return True
    finally:
        conn.close()

