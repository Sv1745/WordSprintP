import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "wordsprint")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def init_db():
    print("==================================================")
    print("WordSprint Database Setup & Initialization")
    print("==================================================")
    print(f"Connecting to PostgreSQL at {DB_HOST}:{DB_PORT} as user '{DB_USER}'...")
    
    # 1. Connect to postgres default DB to check/create target DB
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()
        if not exists:
            print(f"[+] Database '{DB_NAME}' does not exist. Creating database...")
            cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
            print(f"[+] Database '{DB_NAME}' created successfully.")
        else:
            print(f"[OK] Database '{DB_NAME}' already exists.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[!] PostgreSQL default DB check note: {e}")

    # 2. Connect to target wordsprint DB and apply schema & seed data idempotently
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_dir = os.path.join(base_dir, "database")

        sql_files = [
            os.path.join(db_dir, "create_tables.sql"),
            os.path.join(db_dir, "seed_data.sql"),
            os.path.join(db_dir, "seed_words.sql")
        ]

        for sql_file in sql_files:
            if os.path.exists(sql_file):
                print(f"[+] Processing script: {os.path.basename(sql_file)}...")
                with open(sql_file, "r", encoding="utf-8") as f:
                    sql_content = f.read()
                
                # Split statements by semicolon to execute idempotently
                statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]
                for stmt in statements:
                    try:
                        cursor.execute(stmt)
                        conn.commit()
                    except Exception as stmt_err:
                        conn.rollback()
                        err_str = str(stmt_err).lower()
                        if "already exists" in err_str or "duplicate key" in err_str:
                            pass
                        else:
                            print(f"    Notice: {str(stmt_err).strip()}")
                print(f"[OK] Completed {os.path.basename(sql_file)}.")

        cursor.close()
        conn.close()
        print("==================================================")
        print("[SUCCESS] Database setup and data seeding completed successfully!")
        print("==================================================")
    except Exception as e:
        print(f"[ERROR] Failed setting up database schema or seeds: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_db()
