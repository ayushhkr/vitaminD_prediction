"""Reusable preprocessing helpers for the Vitamin D project."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "VitaminD_Dataset.csv"
RANDOM_STATE = 42
DEFICIENCY_THRESHOLD_NG_ML = 20.0

REQUIRED_COLUMNS = [
    "Age",
    "Gender",
    "Weight_kg",
    "Height_cm",
    "BMI",
    "BodyFat_percent",
    "Sun_Exposure_min",
    "Skin_Exposure_percent",
    "Alcohol_units_week",
    "Fish_intake_week",
    "Dairy_intake_week",
    "Physical_activity_hours_week",
    "Indoor_work_hours_day",
    "VitaminD_Level_ng_ml",
]

DROP_IF_PRESENT = [
    "Skin_tone",
    "Sunscreen_Use",
    "VitaminD_Category",
    "Deficiency_Status",
    "Risk_Score",
]


@dataclass(frozen=True)
class DatasetBundle:
    """Prepared feature and target bundle."""

    features: pd.DataFrame
    target: pd.Series


def load_dataset(csv_path: Path | str = DATA_PATH) -> pd.DataFrame:
    """Load the custom Vitamin D CSV."""
    return pd.read_csv(csv_path)


def validate_dataset(df: pd.DataFrame) -> None:
    """Ensure the custom dataset contains the expected columns."""
    missing = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))


def prepare_dataset(df: pd.DataFrame) -> DatasetBundle:
    """Build raw features and target without fitting transforms."""
    validate_dataset(df)

    work = df.copy().drop(columns=DROP_IF_PRESENT, errors="ignore")
    target = pd.to_numeric(work["VitaminD_Level_ng_ml"], errors="coerce")
    if target.isna().any():
        raise ValueError("VitaminD_Level_ng_ml contains non-numeric values.")

    features = work.drop(columns=["VitaminD_Level_ng_ml"])
    return DatasetBundle(features=features, target=target)


def build_preprocessor(features: pd.DataFrame) -> ColumnTransformer:
    """Create a preprocessing pipeline for numeric and categorical features."""
    numeric_columns = features.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_columns = [col for col in features.columns if col not in numeric_columns]

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_columns),
            ("cat", categorical_pipeline, categorical_columns),
        ]
    )
