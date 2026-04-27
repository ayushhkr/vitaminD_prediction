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
        reasons.append("Sun exposure is below 20 min/day, which can reduce natural Vitamin D synthesis.")
    if inputs["Indoor_work_hours_day"] > 8:
        reasons.append("Indoor work time is high, so UV exposure opportunities are limited.")
    if (inputs["Fish_intake_week"] + inputs["Dairy_intake_week"]) < 5:
        reasons.append("Dietary Vitamin D sources look low across fish and dairy intake.")
    if inputs["Physical_activity_hours_week"] < 3:
        reasons.append("Physical activity is on the lower side, which may correlate with less outdoor exposure.")
    if inputs["BMI"] >= 30:
        reasons.append("Higher BMI can be associated with lower circulating Vitamin D levels.")

    if len(reasons) < 2:
        if inputs["Sun_Exposure_min"] >= 30:
            reasons.append(
                f"Sun exposure is {inputs['Sun_Exposure_min']:.0f} min/day, which is generally supportive for Vitamin D production."
            )
        if (inputs["Fish_intake_week"] + inputs["Dairy_intake_week"]) >= 7:
            reasons.append(
                f"Dietary intake is {inputs['Fish_intake_week'] + inputs['Dairy_intake_week']:.0f} servings/week from fish and dairy, supporting intake from food."
            )
        if inputs["Physical_activity_hours_week"] >= 3:
            reasons.append(
                f"Physical activity is {inputs['Physical_activity_hours_week']:.1f} hrs/week, indicating a more active routine."
            )

    if not reasons:
        reasons.append("No major lifestyle risk signal is prominent based on the provided inputs.")

    return reasons[:4]


def build_recommendations(inputs: dict) -> list[str]:
    recommendations = []
    if inputs["Sun_Exposure_min"] < 20:
        recommendations.append("Increase safe daytime sun exposure toward 20-30 minutes on most days.")
    if inputs["Indoor_work_hours_day"] > 8:
        recommendations.append("Add brief daylight breaks during long indoor work periods.")
    if (inputs["Fish_intake_week"] + inputs["Dairy_intake_week"]) < 5:
        recommendations.append("Add more Vitamin D-rich foods such as fatty fish, eggs, and fortified dairy.")
    if inputs["Physical_activity_hours_week"] < 3:
        recommendations.append("Increase weekly activity to at least 3-5 hours, with some outdoor sessions.")

    baseline_actions = [
        "Track progress for 8-12 weeks and recheck Vitamin D through a lab test.",
        "Keep hydration, sleep, and meal timing consistent to support overall recovery and metabolism.",
        "Discuss supplementation with a clinician if levels remain low despite lifestyle changes.",
    ]

    for action in baseline_actions:
        if len(recommendations) >= 3:
            break
        recommendations.append(action)

    return recommendations[:4]


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
