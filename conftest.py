
import os
import psycopg2
import pytest

@pytest.fixture(scope="session", autouse=True)
def reset_db_config_session():
    yield
    try:
        conn = psycopg2.connect(
            dbname="wordsprint",
            user="postgres",
            password=os.environ.get("DB_PASSWORD", "postgres"),
            host="localhost",
            port=5432
        )
        cur = conn.cursor()
        cur.execute("UPDATE game_config SET max_attempts = 5, max_daily_games = 3, game_enabled = TRUE WHERE config_id = 1")
        conn.commit()
        conn.close()
    except Exception:
        pass
