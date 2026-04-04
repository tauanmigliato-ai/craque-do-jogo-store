import sqlite3
from pathlib import Path
from contextlib import contextmanager
from config import settings

DB_PATH = settings.DATABASE_URL
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db_ctx():
    conn = get_db()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    schema = SCHEMA_PATH.read_text()
    with get_db_ctx() as conn:
        conn.executescript(schema)
        # seed default admin
        from auth import hash_password
        cur = conn.execute(
            "SELECT id FROM users WHERE email = ?", ("admin@craquedojogo.com",)
        )
        if not cur.fetchone():
            conn.execute(
                "INSERT INTO users (email, name, password_hash, role) VALUES (?, ?, ?, ?)",
                ("admin@craquedojogo.com", "Admin", hash_password("admin123"), "admin"),
            )


if __name__ == "__main__":
    init_db()
    print("Database initialized.")