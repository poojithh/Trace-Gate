from pathlib import Path
import sqlite3

from config import DATABASE_PATH, SCHEMA_PATH


def get_connection(db_path: str | Path | None = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path is not None else DATABASE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    connection.execute("PRAGMA busy_timeout = 30000;")
    return connection


def initialize_database(db_path: str | Path | None = None) -> None:
    schema_file = Path(SCHEMA_PATH)
    if not schema_file.exists():
        raise FileNotFoundError(f"Database schema not found: {schema_file}")
    path = Path(db_path) if db_path is not None else DATABASE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with get_connection(path) as connection:
        connection.executescript(schema_file.read_text(encoding="utf-8"))
        connection.commit()
