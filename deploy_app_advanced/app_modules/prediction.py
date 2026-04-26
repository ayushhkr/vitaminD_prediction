from pathlib import Path

import joblib
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app_modules.constants import DEFICIENT_CUTOFF, GAUGE_MAX, INSUFFICIENT_CUTOFF


@st.cache_resource
def load_model(model_path: Path):
    return joblib.load(model_path)


def get_status(vitamin_d_value: float) -> str:
    if vitamin_d_value < DEFICIENT_CUTOFF:
        return "Deficient"
    if vitamin_d_value <= INSUFFICIENT_CUTOFF:
        return "Insufficient"
    return "Sufficient"


def build_prediction_input(inputs: dict) -> pd.DataFrame:
    column_order = [
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
    ]
    return pd.DataFrame([inputs])[column_order]


def explain_prediction(inputs: dict) -> list[str]:
    reasons = []
    if inputs["Sun_Exposure_min"] < 20:
        reasons.append("Low sun exposure may lower Vitamin D production.")
    if inputs["Indoor_work_hours_day"] > 8:
        reasons.append("High indoor time may reduce UV exposure.")
    if (inputs["Fish_intake_week"] + inputs["Dairy_intake_week"]) < 5:
        reasons.append("Low diet intake of Vitamin D related foods may contribute.")
    if inputs["Physical_activity_hours_week"] < 3:
        reasons.append("Low physical activity can be associated with lower Vitamin D status.")
    if not reasons:
        reasons.append("Input profile shows generally supportive lifestyle signals for Vitamin D.")
    return reasons


def build_recommendations(inputs: dict) -> list[str]:
    recommendations = []
    if inputs["Sun_Exposure_min"] < 20:
        recommendations.append("Increase safe sunlight exposure during daytime.")
    if (inputs["Fish_intake_week"] + inputs["Dairy_intake_week"]) < 5:
        recommendations.append("Improve diet by adding Vitamin D rich foods like fish, eggs, and fortified dairy.")
    if inputs["Physical_activity_hours_week"] < 3:
        recommendations.append("Increase weekly physical activity with regular outdoor sessions.")
    if not recommendations:
        recommendations.append("Maintain your current lifestyle pattern and monitor Vitamin D periodically.")
    return recommendations


def _bounded_update(base_value: float, delta: float, min_value: float, max_value: float) -> float:
    return float(min(max(base_value + delta, min_value), max_value))


def _predict_value(model_obj, inputs: dict) -> float:
    return float(model_obj.predict(build_prediction_input(inputs))[0])


def summarize_feature_changes(base_inputs: dict, updated_inputs: dict) -> str:
    feature_labels = {
        "Sun_Exposure_min": "Sun Exposure (min/day)",
        "Skin_Exposure_percent": "Skin Exposure (%)",
        "Fish_intake_week": "Fish Intake (/week)",
        "Dairy_intake_week": "Dairy Intake (/week)",
    }

    changes = []
    for key, label in feature_labels.items():
        base_val = float(base_inputs[key])
        updated_val = float(updated_inputs[key])
        if abs(updated_val - base_val) > 1e-9:
            changes.append(f"{label}: {base_val:g} -> {updated_val:g}")

    return " | ".join(changes) if changes else "No feature change"


def build_interpretation_table(model_obj, base_inputs: dict) -> pd.DataFrame:
    baseline_prediction = _predict_value(model_obj, base_inputs)

    sun_inputs = {
        **base_inputs,
        "Sun_Exposure_min": _bounded_update(base_inputs["Sun_Exposure_min"], 20.0, 0.0, 180.0),
        "Skin_Exposure_percent": _bounded_update(base_inputs["Skin_Exposure_percent"], 15.0, 0.0, 100.0),
    }
    diet_inputs = {
        **base_inputs,
        "Fish_intake_week": _bounded_update(base_inputs["Fish_intake_week"], 3.0, 0.0, 14.0),
        "Dairy_intake_week": _bounded_update(base_inputs["Dairy_intake_week"], 3.0, 0.0, 14.0),
    }

    sun_prediction = _predict_value(model_obj, sun_inputs)
    diet_prediction = _predict_value(model_obj, diet_inputs)

    rows = [
        {
            "Scenario": "Current baseline",
            "Feature Changes": "No feature change",
            "Predicted Vitamin D (ng/mL)": round(baseline_prediction, 2),
            "Change vs Baseline (ng/mL)": 0.0,
        },
        {
            "Scenario": "If sun exposure is increased",
            "Feature Changes": summarize_feature_changes(base_inputs, sun_inputs),
            "Predicted Vitamin D (ng/mL)": round(sun_prediction, 2),
            "Change vs Baseline (ng/mL)": round(sun_prediction - baseline_prediction, 2),
        },
        {
            "Scenario": "If diet intake is increased",
            "Feature Changes": summarize_feature_changes(base_inputs, diet_inputs),
            "Predicted Vitamin D (ng/mL)": round(diet_prediction, 2),
            "Change vs Baseline (ng/mL)": round(diet_prediction - baseline_prediction, 2),
        },
    ]

    return pd.DataFrame(rows)


def build_gauge(prediction: float) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=prediction,
            number={"suffix": " ng/mL"},
            gauge={
                "axis": {"range": [0, GAUGE_MAX]},
                "bar": {"color": "#2563eb"},
                "steps": [
                    {"range": [0, DEFICIENT_CUTOFF], "color": "#fecaca"},
                    {"range": [DEFICIENT_CUTOFF, INSUFFICIENT_CUTOFF], "color": "#fde68a"},
                    {"range": [INSUFFICIENT_CUTOFF, GAUGE_MAX], "color": "#bbf7d0"},
                ],
            },
        )
    )
    fig.update_layout(height=205, margin={"l": 8, "r": 8, "t": 16, "b": 6})
    return fig
