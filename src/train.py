"""Training script for the advanced Vitamin D project."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline

from preprocessing import (
    DATA_PATH,
    DEFICIENCY_THRESHOLD_NG_ML,
    PROJECT_ROOT,
    RANDOM_STATE,
    build_preprocessor,
    load_dataset,
    prepare_dataset,
)

try:
    from xgboost import XGBRegressor
except Exception:
    XGBRegressor = None


MODELS_DIR = PROJECT_ROOT / "artifacts" / "models"
METRICS_DIR = PROJECT_ROOT / "artifacts" / "metrics"


def _binary_metrics(y_true: pd.Series, y_pred: np.ndarray, y_score: np.ndarray) -> dict[str, float]:
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    sensitivity = tp / (tp + fn) if (tp + fn) else 0.0
    specificity = tn / (tn + fp) if (tn + fp) else 0.0
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_score)),
        "sensitivity": float(sensitivity),
        "specificity": float(specificity),
    }


def build_regression_models(features: pd.DataFrame) -> dict[str, Pipeline]:
    """Create the model set used in the advanced version."""
    preprocessor = build_preprocessor(features)
    models: dict[str, object] = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=300,
            random_state=RANDOM_STATE,
            min_samples_leaf=2,
            n_jobs=1,
        ),
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=3,
            random_state=RANDOM_STATE,
        ),
    }
    if XGBRegressor is not None:
        models["XGBoost"] = XGBRegressor(
            n_estimators=400,
            learning_rate=0.05,
            max_depth=4,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=RANDOM_STATE,
            objective="reg:squarederror",
            eval_metric="rmse",
            n_jobs=1,
        )

    return {
        name: Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", model),
            ]
        )
        for name, model in models.items()
    }


def build_classifier(features: pd.DataFrame) -> Pipeline:
    """Create the direct deficiency classifier."""
    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor(features)),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=300,
                    random_state=RANDOM_STATE,
                    min_samples_leaf=2,
                    n_jobs=1,
                ),
            ),
        ]
    )


def train_and_save(data_path: Path | str = DATA_PATH) -> tuple[str, pd.DataFrame, dict[str, float]]:
    """Run training and save advanced project artifacts."""
    bundle = prepare_dataset(load_dataset(data_path))
    X_train, X_test, y_train, y_test = train_test_split(
        bundle.features,
        bundle.target,
        test_size=0.2,
        random_state=RANDOM_STATE,
    )

    scoring = {
        "r2": "r2",
        "neg_mae": "neg_mean_absolute_error",
        "neg_rmse": "neg_root_mean_squared_error",
    }

    rows: list[dict[str, float | str]] = []
    test_predictions = pd.DataFrame({"actual_vitamin_d_ng_ml": y_test}).reset_index(drop=True)
    best_model = None
    best_model_name = ""
    best_cv_r2 = -np.inf

    for name, pipeline in build_regression_models(bundle.features).items():
        cv = cross_validate(
            pipeline,
            X_train,
            y_train,
            cv=5,
            scoring=scoring,
            n_jobs=1,
        )
        pipeline.fit(X_train, y_train)
        preds = pipeline.predict(X_test)

        row = {
            "model": name,
            "test_r2": float(r2_score(y_test, preds)),
            "test_mae": float(mean_absolute_error(y_test, preds)),
            "test_rmse": float(np.sqrt(mean_squared_error(y_test, preds))),
            "cv_r2_mean": float(np.mean(cv["test_r2"])),
            "cv_r2_std": float(np.std(cv["test_r2"])),
            "cv_mae_mean": float(-np.mean(cv["test_neg_mae"])),
            "cv_rmse_mean": float(-np.mean(cv["test_neg_rmse"])),
        }
        rows.append(row)
        test_predictions[f"{name.lower().replace(' ', '_')}_prediction"] = preds

        if row["cv_r2_mean"] > best_cv_r2:
            best_cv_r2 = row["cv_r2_mean"]
            best_model_name = name
            best_model = pipeline

    if best_model is None:
        raise RuntimeError("Training did not produce a best model.")

    regression_metrics = pd.DataFrame(rows).sort_values(
        by=["cv_r2_mean", "test_r2"],
        ascending=False,
    ).reset_index(drop=True)

    y_test_binary = (y_test < DEFICIENCY_THRESHOLD_NG_ML).astype(int)
    reg_preds = best_model.predict(X_test)
    reg_binary = (reg_preds < DEFICIENCY_THRESHOLD_NG_ML).astype(int)
    reg_scores = -reg_preds
    reg_binary_metrics = _binary_metrics(y_test_binary, reg_binary, reg_scores)

    classifier = build_classifier(bundle.features)
    y_binary = (bundle.target < DEFICIENCY_THRESHOLD_NG_ML).astype(int)
    X_cls_train, X_cls_test, y_cls_train, y_cls_test = train_test_split(
        bundle.features,
        y_binary,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y_binary,
    )
    classifier.fit(X_cls_train, y_cls_train)
    cls_prob = classifier.predict_proba(X_cls_test)[:, 1]
    cls_pred = (cls_prob >= 0.5).astype(int)
    cls_metrics = _binary_metrics(y_cls_test, cls_pred, cls_prob)

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cls_cv = cross_validate(
        classifier,
        X_cls_train,
        y_cls_train,
        cv=skf,
        scoring={"roc_auc": "roc_auc", "f1": "f1", "accuracy": "accuracy"},
        n_jobs=1,
    )

    summary = {
        "best_model_name": best_model_name,
        "feature_columns": bundle.features.columns.tolist(),
        "classification_results": {
            "threshold_ng_ml": DEFICIENCY_THRESHOLD_NG_ML,
            "regression_then_threshold_accuracy": reg_binary_metrics["accuracy"],
            "regression_then_threshold_f1": reg_binary_metrics["f1"],
            "regression_then_threshold_roc_auc": reg_binary_metrics["roc_auc"],
            "regression_then_threshold_sensitivity": reg_binary_metrics["sensitivity"],
            "regression_then_threshold_specificity": reg_binary_metrics["specificity"],
            "direct_classification_accuracy": cls_metrics["accuracy"],
            "direct_classification_f1": cls_metrics["f1"],
            "direct_classification_roc_auc": cls_metrics["roc_auc"],
            "direct_classification_sensitivity": cls_metrics["sensitivity"],
            "direct_classification_specificity": cls_metrics["specificity"],
            "direct_classification_cv_roc_auc_mean": float(np.mean(cls_cv["test_roc_auc"])),
            "direct_classification_cv_f1_mean": float(np.mean(cls_cv["test_f1"])),
            "direct_classification_cv_accuracy_mean": float(np.mean(cls_cv["test_accuracy"])),
        },
    }

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, MODELS_DIR / "best_model.joblib")
    regression_metrics.to_csv(METRICS_DIR / "regression_metrics.csv", index=False)
    test_predictions.to_csv(METRICS_DIR / "test_predictions.csv", index=False)
    (METRICS_DIR / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return best_model_name, regression_metrics, summary["classification_results"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the advanced Vitamin D project.")
    parser.add_argument(
        "--data",
        default=str(DATA_PATH),
        help="Path to the custom dataset CSV file.",
    )
    args = parser.parse_args()

    best_model_name, regression_metrics, classification_results = train_and_save(args.data)
    print("Best model:", best_model_name)
    print()
    print(regression_metrics.to_string(index=False))
    print()
    print("Classification summary:")
    for key, value in classification_results.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
