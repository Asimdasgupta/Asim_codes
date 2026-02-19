from __future__ import annotations

import math
from typing import Any

import pandas as pd


def bmi_from_profile(profile: dict) -> float | None:
    weight = profile.get("weight_kg")
    height_cm = profile.get("height_cm")
    if weight is None or height_cm is None:
        return None
    try:
        h_m = float(height_cm) / 100.0
        if h_m <= 0:
            return None
        return float(weight) / (h_m * h_m)
    except (TypeError, ValueError):
        return None


def safe_float(x: Any) -> float | None:
    if x is None:
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def safe_int(x: Any) -> int | None:
    if x is None:
        return None
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def compute_rolling_mean(series: pd.Series, window: int) -> float | None:
    if series is None or series.empty:
        return None
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return None
    return float(s.tail(window).mean())


def build_feature_row(profile: dict, entry: dict, recent_entries: list[dict]) -> dict[str, float]:
    df = pd.DataFrame(recent_entries) if recent_entries else pd.DataFrame()
    if not df.empty and "entry_date" in df.columns:
        df = df.sort_values("entry_date")

    bmi = bmi_from_profile(profile)

    features: dict[str, float] = {}

    age = safe_float(profile.get("age"))
    if age is not None:
        features["age"] = age

    if bmi is not None and not math.isnan(bmi):
        features["bmi"] = float(bmi)

    bp_sys = safe_float(entry.get("bp_systolic") or profile.get("bp_systolic"))
    bp_dia = safe_float(entry.get("bp_diastolic") or profile.get("bp_diastolic"))
    sugar = safe_float(entry.get("sugar_mg_dl") or profile.get("sugar_mg_dl"))

    if bp_sys is not None:
        features["bp_systolic"] = bp_sys
    if bp_dia is not None:
        features["bp_diastolic"] = bp_dia
    if sugar is not None:
        features["sugar_mg_dl"] = sugar

    for k in [
        "steps",
        "sleep_hours",
        "heart_rate",
        "calories",
        "activity_minutes",
        "sleep_quality",
        "mood",
        "stress",
        "pain",
    ]:
        v = safe_float(entry.get(k))
        if v is not None:
            features[k] = v

    symptoms = entry.get("symptoms")
    if isinstance(symptoms, list):
        features["symptoms_count"] = float(len(symptoms))

    if not df.empty:
        if "sleep_hours" in df.columns:
            m = compute_rolling_mean(df["sleep_hours"], 7)
            if m is not None:
                features["avg_sleep_7d"] = m
        if "steps" in df.columns:
            m = compute_rolling_mean(df["steps"], 7)
            if m is not None:
                features["avg_steps_7d"] = m
        if "heart_rate" in df.columns:
            m = compute_rolling_mean(df["heart_rate"], 7)
            if m is not None:
                features["avg_hr_7d"] = m

    return features

