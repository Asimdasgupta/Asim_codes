# Local Health Monitoring Web App (Local-First)

A beginner-friendly local web app to:
- collect medical history + daily wellness data
- compress + store it in SQLite (plus optional JSON export)
- run a lightweight scikit-learn model locally
- show simple recommendations in a clean HTML/CSS UI

## 1) Folder Structure

```
local-health-monitoring-app/
  app.py
  requirements.txt
  README.md
  instance/
    health.db            # created automatically
  data/
    sample_profile.json
    sample_daily_entries.csv
    sample_training_data.csv
  scripts/
    init_db.py
    seed_db.py
    train_model.py
  health_app/
    __init__.py
    db.py
    schema.sql
    compress.py
    features.py
    ml.py
    recommendations.py
    repo.py
    utils.py
  templates/
    base.html
    dashboard.html
    profile.html
    checkin.html
  static/
    styles.css
```

## 2) Setup & Run

### 2.1 Create a virtual environment (recommended)

From `local-health-monitoring-app/`:

```bash
python -m venv .venv
```

Activate:

- PowerShell:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```

### 2.2 Install dependencies

```bash
pip install -r requirements.txt
```

### 2.3 Initialize DB + load sample data

```bash
python scripts/init_db.py
python scripts/seed_db.py
```

### 2.4 Train the lightweight model (optional but recommended)

```bash
python scripts/train_model.py
```

### 2.5 Start the server

```bash
python scripts/run_server.py
```

Open:
- http://127.0.0.1:8000/

### Windows easiest way

Double-click `run_windows.bat` (it creates venv, installs deps, seeds DB, and opens the browser).

### If the browser says “Service Unavailable”

That usually means the server is not running (or you closed the terminal that was running it).
Start it again with `python app.py` and keep that terminal open.

You can change host/port:

```powershell
$env:HOST = "127.0.0.1"
$env:PORT = "8000"
python app.py
```

## 3) What “Compression” Means Here

This project reduces processing cost in two ways:

1) **Data summarization**
   - The app computes compact daily features (e.g., BMI, 7-day average steps/sleep) and stores those.
   - The ML model uses only these summary features, so it doesn’t scan all raw history for every prediction.

2) **Feature reduction (feature selection)**
   - During training, the app runs a simple feature selection step to keep only the most useful columns.
   - Fewer features = smaller matrices, faster training/inference, and lower memory use.

3) **Lightweight storage + compression**
   - Raw medical/profile data and raw daily entries are stored as JSON **and** as a compressed BLOB (zlib) in SQLite.
   - This reduces disk size and speeds up I/O when exporting/importing.

The key idea: **your model never needs heavy deep learning** and **the app never needs cloud**.

## 4) Safety Note

This app is an educational demo. Recommendations are general wellness suggestions, not medical advice.
