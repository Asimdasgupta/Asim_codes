from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression

from .features import build_feature_row


DEFAULT_FEATURES: list[str] = [
    "age",
    "bmi",
    "bp_systolic",
    "bp_diastolic",
    "sugar_mg_dl",
    "steps",
    "sleep_hours",
    "heart_rate",
    "calories",
    "activity_minutes",
    "sleep_quality",
    "mood",
    "stress",
    "pain",
    "symptoms_count",
    "avg_sleep_7d",
    "avg_steps_7d",
    "avg_hr_7d",
]


@dataclass
class ModelBundle:
    features: list[str]
    selected_features: list[str]
    selector: SelectKBest
    model: LogisticRegression


def load_model_bundle(model_path: Path) -> ModelBundle | None:
    if not model_path.exists():
        return None
    obj = joblib.load(model_path)
    return ModelBundle(
        features=obj["features"],
        selected_features=obj["selected_features"],
        selector=obj["selector"],
        model=obj["model"],
    )


def _row_to_vector(features: list[str], row: dict) -> np.ndarray:
    vec = []
    for f in features:
        v = row.get(f)
        if v is None or (isinstance(v, float) and np.isnan(v)):
            vec.append(0.0)
        else:
            vec.append(float(v))
    return np.array(vec, dtype=np.float32)


def train_model_from_csv(csv_path: Path, model_path: Path, k_best: int = 10) -> ModelBundle:
    df = pd.read_csv(csv_path)
    if "label" not in df.columns:
        raise ValueError("Training CSV must include a 'label' column")

    features = [c for c in DEFAULT_FEATURES if c in df.columns]
    X = df[features].fillna(0.0).astype(np.float32).to_numpy()
    y = df["label"].astype(int).to_numpy()

    k = min(k_best, max(1, len(features)))
    selector = SelectKBest(score_func=f_classif, k=k)
    X_sel = selector.fit_transform(X, y)

    model = LogisticRegression(max_iter=500)
    model.fit(X_sel, y)

    support = selector.get_support()
    selected_features = [f for f, keep in zip(features, support) if keep]

    bundle = ModelBundle(
        features=features,
        selected_features=selected_features,
        selector=selector,
        model=model,
    )

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "features": bundle.features,
            "selected_features": bundle.selected_features,
            "selector": bundle.selector,
            "model": bundle.model,
        },
        model_path,
    )
    return bundle


def predict_risk(bundle: ModelBundle, profile: dict, entry: dict, recent_entries: list[dict]) -> float:
    row = build_feature_row(profile, entry, recent_entries)
    x = _row_to_vector(bundle.features, row).reshape(1, -1)
    x_sel = bundle.selector.transform(x)
    prob = float(bundle.model.predict_proba(x_sel)[0][1])
    return prob

