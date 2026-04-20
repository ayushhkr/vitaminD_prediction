"""Evaluation helpers for reviewing saved metrics and making one prediction."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd

from preprocessing import DATA_PATH, DEFICIENCY_THRESHOLD_NG_ML, PROJECT_ROOT, load_dataset


MODELS_DIR = PROJECT_ROOT / "artifacts" / "models"
METRICS_DIR = PROJECT_ROOT / "artifacts" / "metrics"


def show_saved_metrics() -> None:
    """Print the saved training outputs."""
    metrics_path = METRICS_DIR / "regression_metrics.csv"
    summary_path = METRICS_DIR / "run_summary.json"

    if not metrics_path.exists() or not summary_path.exists():
        raise FileNotFoundError("Saved metrics were not found. Run src/train.py first.")

    regression_metrics = pd.read_csv(metrics_path)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    print("Regression metrics:")
    print(regression_metrics.to_string(index=False))
    print()
    print("Run summary:")
    print(json.dumps(summary, indent=2))


def predict_sample() -> None:
    """Run one sample prediction from the saved best model."""
    model_path = MODELS_DIR / "best_model.joblib"
    if not model_path.exists():
        raise FileNotFoundError("Saved model not found. Run src/train.py first.")

    model = joblib.load(model_path)
    sample = pd.DataFrame(
        {
            "Age": [25],
            "Gender": [1],
            "Weight_kg": [72],
            "Height_cm": [170],
            "BMI": [24],
            "BodyFat_percent": [18],
            "Sun_Exposure_min": [25],
            "Skin_Exposure_percent": [40],
            "Alcohol_units_week": [0],
            "Fish_intake_week": [1],
            "Dairy_intake_week": [5],
            "Physical_activity_hours_week": [3],
            "Indoor_work_hours_day": [6],
        }
    )
    prediction = float(model.predict(sample)[0])
    label = "Deficient" if prediction < DEFICIENCY_THRESHOLD_NG_ML else "Not Deficient"

    print("Sample prediction (ng/mL):", round(prediction, 2))
    print("Deficiency label:", label)


def main() -> None:
    parser = argparse.ArgumentParser(description="Review saved metrics or run a sample prediction.")
    parser.add_argument(
        "--mode",
        choices=["metrics", "predict"],
        default="metrics",
        help="Choose whether to print saved metrics or run a sample prediction.",
    )
    parser.add_argument(
        "--data",
        default=str(DATA_PATH),
        help="Unused placeholder path for consistency with the project structure.",
    )
    args = parser.parse_args()

    _ = load_dataset(args.data)
    if args.mode == "metrics":
        show_saved_metrics()
    else:
        predict_sample()


if __name__ == "__main__":
    main()
