from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from health_app.db import ensure_db
from health_app.repo import save_daily_entry, save_profile


def main() -> None:
    db_path = BASE_DIR / "instance" / "health.db"
    ensure_db(db_path)

    profile_path = BASE_DIR / "data" / "sample_profile.json"
    save_profile(db_path, json.loads(profile_path.read_text(encoding="utf-8")))

    entries_path = BASE_DIR / "data" / "sample_daily_entries.csv"
    with entries_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            payload = {
                "entry_date": row.get("entry_date"),
                "steps": row.get("steps"),
                "sleep_hours": row.get("sleep_hours"),
                "heart_rate": row.get("heart_rate"),
                "calories": row.get("calories"),
                "activity_minutes": row.get("activity_minutes"),
                "sleep_quality": row.get("sleep_quality"),
                "mood": row.get("mood"),
                "stress": row.get("stress"),
                "pain": row.get("pain"),
                "bp_systolic": row.get("bp_systolic"),
                "bp_diastolic": row.get("bp_diastolic"),
                "sugar_mg_dl": row.get("sugar_mg_dl"),
                "notes": row.get("notes"),
            }
            save_daily_entry(db_path, payload)

    print("Seeded sample profile + entries into SQLite.")


if __name__ == "__main__":
    main()
