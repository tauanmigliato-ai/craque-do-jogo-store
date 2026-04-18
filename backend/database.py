import sqlite3
from pathlib import Path
from contextlib import contextmanager
from config import settings

DB_PATH = settings.DATABASE_URL
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def _configure(conn: sqlite3.Connection) -> None:
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")


def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    _configure(conn)
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


@contextmanager
def get_db_exclusive():
    """Transação com BEGIN IMMEDIATE — evita race condition em operações críticas (ex: estoque)."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, isolation_level=None)
    _configure(conn)
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()


def init_db():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    schema = SCHEMA_PATH.read_text()
    with get_db_ctx() as conn:
        conn.executescript(schema)
        if settings.ADMIN_PASSWORD:
            from auth import hash_password
            conn.execute(
                "INSERT OR IGNORE INTO users (email, name, password_hash, role) VALUES (?, ?, ?, ?)",
                (settings.ADMIN_EMAIL, "Admin", hash_password(settings.ADMIN_PASSWORD), "admin"),
            )


if __name__ == "__main__":
    init_db()
    print("Database initialized.")
