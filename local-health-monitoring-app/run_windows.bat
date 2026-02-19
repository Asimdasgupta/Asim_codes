@echo off
setlocal

cd /d %~dp0

if not exist .venv\Scripts\python.exe (
  python -m venv .venv
)

call .venv\Scripts\activate.bat

python -m pip install -r requirements.txt
python scripts\init_db.py
python scripts\seed_db.py

start "" http://127.0.0.1:8000/
python app.py

