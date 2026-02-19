from __future__ import annotations

import sqlite3
from pathlib import Path


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def ensure_db(db_path: Path) -> None:
    schema_path = Path(__file__).resolve().parent / "schema.sql"
    with connect(db_path) as conn:
        conn.executescript(schema_path.read_text(encoding="utf-8"))
        conn.execute(
            "INSERT OR IGNORE INTO medical_profile (id, updated_at, json_blob) VALUES (?, datetime('now'), ?)",
            ("local", "{}"),
        )
        conn.commit()

