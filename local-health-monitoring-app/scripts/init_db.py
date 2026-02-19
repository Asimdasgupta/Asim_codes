from __future__ import annotations

from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from health_app.db import ensure_db


def main() -> None:
    db_path = BASE_DIR / "instance" / "health.db"
    ensure_db(db_path)
    print(f"Initialized SQLite DB at: {db_path}")


if __name__ == "__main__":
    main()
