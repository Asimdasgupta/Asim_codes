from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd

from .compress import compress_json, decompress_json
from .db import connect
from .features import build_feature_row


def get_profile(db_path: Path) -> dict:
    with connect(db_path) as conn:
        row = conn.execute("SELECT json_blob_compressed, json_blob FROM medical_profile WHERE id='local'").fetchone()
        if row is None:
            return {}
        if row["json_blob_compressed"] is not None:
            return decompress_json(row["json_blob_compressed"])
        return json.loads(row["json_blob"] or "{}")


def save_profile(db_path: Path, profile: dict) -> None:
    json_text, compressed = compress_json(profile)
    with connect(db_path) as conn:
        conn.execute(
            "UPDATE medical_profile SET updated_at=datetime('now'), json_blob=?, json_blob_compressed=? WHERE id='local'",
            (json_text, sqlite3.Binary(compressed)),
        )
        conn.commit()


def list_recent_entries(db_path: Path, limit: int = 30) -> list[dict]:
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT json_blob_compressed, json_blob FROM daily_entry ORDER BY entry_date DESC, created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()

    out: list[dict] = []
    for r in rows:
        if r["json_blob_compressed"] is not None:
            out.append(decompress_json(r["json_blob_compressed"]))
        else:
            out.append(json.loads(r["json_blob"] or "{}"))
    return out


def get_latest_entry(db_path: Path) -> dict | None:
    items = list_recent_entries(db_path, limit=1)
    return items[0] if items else None


def save_daily_entry(db_path: Path, entry: dict) -> tuple[bool, str]:
    entry_date = (entry.get("entry_date") or "").strip()
    if entry_date == "":
        return False, "Please pick a date for the check-in."

    entry_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat(timespec="seconds")
    stored = {"id": entry_id, "created_at": now, **entry}
    json_text, compressed = compress_json(stored)

    with connect(db_path) as conn:
        conn.execute(
            "INSERT INTO daily_entry (id, entry_date, created_at, json_blob, json_blob_compressed) VALUES (?, ?, ?, ?, ?)",
            (entry_id, entry_date, now, json_text, sqlite3.Binary(compressed)),
        )
        conn.commit()

    profile = get_profile(db_path)
    recent = list_recent_entries(db_path, limit=30)
    features = build_feature_row(profile, stored, recent)
    feat_json, feat_compressed = compress_json(features)
    with connect(db_path) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO daily_entry_features (entry_id, created_at, features_json, features_json_compressed) VALUES (?, ?, ?, ?)",
            (entry_id, now, feat_json, sqlite3.Binary(feat_compressed)),
        )
        conn.commit()

    return True, "ok"


def export_all_data(db_path: Path) -> str:
    profile = get_profile(db_path)
    entries = list_recent_entries(db_path, limit=3650)
    payload = {"profile": profile, "entries": entries}
    return json.dumps(payload, ensure_ascii=False, indent=2)


def entries_to_dataframe(entries: list[dict]) -> pd.DataFrame:
    if not entries:
        return pd.DataFrame()

    df = pd.DataFrame(entries)
    cols = {
        "steps": "Int32",
        "heart_rate": "Int16",
        "calories": "Int32",
        "activity_minutes": "Int16",
        "sleep_quality": "Int8",
        "mood": "Int8",
        "stress": "Int8",
        "pain": "Int8",
        "bp_systolic": "Int16",
        "bp_diastolic": "Int16",
    }
    for c, dtype in cols.items():
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype(dtype)

    for c in ["sleep_hours", "sugar_mg_dl"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("Float32")

    if "entry_date" in df.columns:
        df["entry_date"] = pd.to_datetime(df["entry_date"], errors="coerce")

    return df
