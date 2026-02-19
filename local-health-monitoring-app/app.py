from __future__ import annotations

from pathlib import Path
import os

from flask import Flask, flash, redirect, render_template, request, url_for

from health_app.db import ensure_db
from health_app.ml import load_model_bundle, predict_risk, train_model_from_csv
from health_app.recommendations import build_recommendations
from health_app.repo import (
    export_all_data,
    get_latest_entry,
    get_profile,
    list_recent_entries,
    save_daily_entry,
    save_profile,
)
from health_app.utils import parse_float, parse_int


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = "local-dev-secret"  

    base_dir = Path(__file__).resolve().parent
    db_path = base_dir / "instance" / "health.db"
    model_path = base_dir / "instance" / "model_bundle.joblib"

    ensure_db(db_path)

    @app.get("/@vite/client")
    def vite_client():
        return ("", 204)

    @app.get("/@react-refresh")
    def react_refresh():
        return ("", 204)

    @app.get("/")
    def dashboard():
        profile = get_profile(db_path)
        latest = get_latest_entry(db_path)
        recent = list_recent_entries(db_path, limit=30)

        model_bundle = load_model_bundle(model_path)
        model_score = None
        if latest is not None and model_bundle is not None:
            model_score = predict_risk(model_bundle, profile, latest, recent)

        recos = build_recommendations(profile, latest, model_score)
        return render_template(
            "dashboard.html",
            profile=profile,
            latest=latest,
            recent=recent,
            model_score=model_score,
            model_trained=model_bundle is not None,
            recommendations=recos,
        )

    @app.post("/train")
    def train():
        csv_path = base_dir / "data" / "sample_training_data.csv"
        try:
            bundle = train_model_from_csv(csv_path, model_path, k_best=10)
        except Exception as e:
            flash(f"Training failed: {e}")
            return redirect(url_for("dashboard"))

        flash(f"Model trained locally. Selected {len(bundle.selected_features)} features.")
        return redirect(url_for("dashboard"))

    @app.get("/profile")
    def profile_page():
        profile = get_profile(db_path)
        return render_template("profile.html", profile=profile)

    @app.post("/profile")
    def profile_save():
        payload = {
            "age": parse_int(request.form.get("age")),
            "weight_kg": parse_float(request.form.get("weight_kg")),
            "height_cm": parse_float(request.form.get("height_cm")),
            "bp_systolic": parse_int(request.form.get("bp_systolic")),
            "bp_diastolic": parse_int(request.form.get("bp_diastolic")),
            "sugar_mg_dl": parse_float(request.form.get("sugar_mg_dl")),
            "past_diseases": request.form.get("past_diseases", "").strip(),
            "medications": request.form.get("medications", "").strip(),
            "notes": request.form.get("notes", "").strip(),
        }
        save_profile(db_path, payload)
        flash("Profile saved locally.")
        return redirect(url_for("profile_page"))

    @app.get("/checkin")
    def checkin_page():
        return render_template("checkin.html")

    @app.post("/checkin")
    def checkin_save():
        payload = {
            "entry_date": request.form.get("entry_date"),
            "steps": parse_int(request.form.get("steps")),
            "sleep_hours": parse_float(request.form.get("sleep_hours")),
            "heart_rate": parse_int(request.form.get("heart_rate")),
            "calories": parse_int(request.form.get("calories")),
            "activity_minutes": parse_int(request.form.get("activity_minutes")),
            "sleep_quality": parse_int(request.form.get("sleep_quality")),
            "mood": parse_int(request.form.get("mood")),
            "stress": parse_int(request.form.get("stress")),
            "pain": parse_int(request.form.get("pain")),
            "bp_systolic": parse_int(request.form.get("bp_systolic")),
            "bp_diastolic": parse_int(request.form.get("bp_diastolic")),
            "sugar_mg_dl": parse_float(request.form.get("sugar_mg_dl")),
            "notes": request.form.get("notes", "").strip(),
        }
        ok, msg = save_daily_entry(db_path, payload)
        if not ok:
            flash(msg)
            return redirect(url_for("checkin_page"))

        flash("Check-in saved locally.")
        return redirect(url_for("dashboard"))

    @app.get("/export")
    def export_data():
        data = export_all_data(db_path)
        return app.response_class(
            response=data,
            status=200,
            mimetype="application/json",
            headers={"Content-Disposition": "attachment; filename=health_export.json"},
        )

    return app


if __name__ == "__main__":
    app = create_app()
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    app.run(host=host, port=port, debug=False, use_reloader=False)
