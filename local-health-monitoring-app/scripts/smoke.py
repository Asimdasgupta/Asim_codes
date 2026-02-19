from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))


def main() -> None:
    import flask
    import pandas
    import sklearn

    from app import create_app

    app = create_app()
    print("imports_ok")
    print("flask", flask.__version__)
    print("pandas", pandas.__version__)
    print("sklearn", sklearn.__version__)
    print("routes", len(list(app.url_map.iter_rules())))


if __name__ == "__main__":
    main()
