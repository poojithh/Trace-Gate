import json
import sqlite3
import pytest

from database.connection import get_connection, initialize_database


def seed_application(conn):
    conn.execute(
        "INSERT INTO vendors VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("v1", "Example Supplies Ltd", "India", "Private Limited", "Equipment",
         "Asha Rao", "asha@example.test", "9000000000",
         "2026-11-02T10:00:00Z", "2026-11-02T10:00:00Z")
    )
    conn.execute(
        "INSERT INTO applications VALUES (?, ?, ?, ?, ?)",
        ("a1", "v1", "DRAFT", "2026-11-02T10:00:00Z", "2026-11-02T10:00:00Z")
    )


def test_initialization_is_repeatable(tmp_path):
    db = tmp_path / "tracegate_test.db"
    initialize_database(db)
    initialize_database(db)
    with get_connection(db) as conn:
        tables = {r["name"] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"vendors", "applications", "submission_versions", "documents",
            "validation_results", "correction_items", "review_records",
            "audit_logs"}.issubset(tables)


def test_foreign_keys_enabled(tmp_path):
    db = tmp_path / "tracegate_test.db"
    initialize_database(db)
    with get_connection(db) as conn:
        assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_duplicate_version_number_rejected(tmp_path):
    db = tmp_path / "tracegate_test.db"
    initialize_database(db)
    with get_connection(db) as conn:
        seed_application(conn)
        payload = json.dumps({"company_name": "Example Supplies Ltd"})
        conn.execute("INSERT INTO submission_versions VALUES (?, ?, ?, ?, ?)",
                     ("ver1", "a1", 1, payload, "2026-11-02T10:00:00Z"))
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO submission_versions VALUES (?, ?, ?, ?, ?)",
                         ("ver2", "a1", 1, payload, "2026-11-02T10:05:00Z"))


def test_invalid_foreign_key_rejected(tmp_path):
    db = tmp_path / "tracegate_test.db"
    initialize_database(db)
    with get_connection(db) as conn:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO applications VALUES (?, ?, ?, ?, ?)",
                         ("a1", "missing-vendor", "DRAFT",
                          "2026-11-02T10:00:00Z", "2026-11-02T10:00:00Z"))


def test_submission_version_is_immutable(tmp_path):
    db = tmp_path / "tracegate_test.db"
    initialize_database(db)
    with get_connection(db) as conn:
        seed_application(conn)
        conn.execute("INSERT INTO submission_versions VALUES (?, ?, ?, ?, ?)",
                     ("ver1", "a1", 1, json.dumps({"name": "Original"}),
                      "2026-11-02T10:00:00Z"))
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            conn.execute("UPDATE submission_versions SET submitted_data=? WHERE version_id=?",
                         (json.dumps({"name": "Changed"}), "ver1"))
