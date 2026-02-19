from __future__ import annotations

from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from health_app.ml import train_model_from_csv


def main() -> None:
    csv_path = BASE_DIR / "data" / "sample_training_data.csv"
    model_path = BASE_DIR / "instance" / "model_bundle.joblib"
    bundle = train_model_from_csv(csv_path, model_path, k_best=10)
    print(f"Trained model. Selected features: {bundle.selected_features}")
    print(f"Saved model bundle to: {model_path}")


if __name__ == "__main__":
    main()
