from pathlib import Path

import joblib
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


MODEL_PATH = Path(__file__).resolve().parent / "advanced_model.pkl"
DEFICIENT_CUTOFF = 20.0
INSUFFICIENT_CUTOFF = 30.0
GAUGE_MAX = 60.0


st.set_page_config(
    page_title="Vitamin D AI Prediction System - Advanced",
    page_icon="D",
    layout="centered",
)

st.markdown(
    """
    <style>
    :root {
        --bg: #f6e6d5;
        --surface: #fff2e2;
        --card: #fffbf5;
        --border: #dcbfa2;
        --text: #3b2416;
        --muted: #7a5034;
        --primary: #c76b2a;
        --primary-strong: #a6521f;
        --success: #8a5a2b;
        --warning: #b36a1e;
        --danger: #9e3a22;
    }
    .stApp {
        background: linear-gradient(180deg, #f9ecdf 0%, var(--bg) 65%, #f3deca 100%);
        color: var(--text);
    }
    [data-testid="stAppViewContainer"] {
        background: transparent;
        color: var(--text);
    }
    .block-container {
        max-width: 760px;
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        background: transparent;
    }
    .card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1rem 1rem 0.75rem 1rem;
        margin-bottom: 0.9rem;
        box-shadow: 0 6px 22px rgba(15, 23, 42, 0.06);
    }
    .small-note {
        color: var(--muted);
        font-size: 0.9rem;
        margin-top: 0.3rem;
    }
    h1, h2, h3 {
        color: var(--text) !important;
        letter-spacing: -0.01em;
    }
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] div,
    [data-testid="stRadio"] label,
    [data-testid="stSelectbox"] label,
    [data-testid="stSlider"] label,
    [data-testid="stNumberInput"] label {
        color: var(--text) !important;
    }
    [data-testid="stCaptionContainer"] {
        color: var(--muted) !important;
    }
    p, label, span, div {
        color: var(--text);
    }
    [data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.75rem;
    }
    [data-testid="stMetricLabel"] {
        color: var(--muted) !important;
    }
    [data-testid="stMetricValue"] {
        color: var(--text) !important;
    }
    [data-testid="stVerticalBlock"] [data-testid="stMarkdownContainer"] p {
        color: var(--text);
    }
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-strong) 100%);
        color: #ffffff;
        border: 1px solid var(--primary-strong);
        border-radius: 10px;
        font-weight: 600;
    }
    .stButton > button:hover {
        filter: brightness(1.03);
    }
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {
        border: 1px solid var(--border) !important;
        background: #fffdf7 !important;
        color: var(--text) !important;
    }
    div[data-baseweb="popover"] * {
        color: var(--text) !important;
        background: #fff8ee !important;
    }
    .stSlider [data-baseweb="slider"] {
        color: var(--primary-strong);
    }
    .stPlotlyChart {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.25rem 0.4rem;
    }
    [data-testid="stAlert"] {
        color: var(--text) !important;
        border-color: var(--border) !important;
        background: #fff6ea !important;
    }
    .stDataFrame, [data-testid="stDataFrame"] * {
        color: var(--text) !important;
    }
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 10px;
        overflow: hidden;
    }
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.9rem;
            padding-right: 0.9rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


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
        "Physical_activity_hours_week": "Physical Activity (hrs/week)",
        "Indoor_work_hours_day": "Indoor Work (hrs/day)",
        "Alcohol_units_week": "Alcohol Units (/week)",
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


def generate_agentic_recommendations(model_obj, base_inputs: dict) -> tuple[list[dict], list[str]]:
    """
    Agentic pipeline:
    1) Build intervention scenarios
    2) Re-run model for each scenario
    3) Rank by predicted improvement
    4) Return ranked impacts and action plan
    """
    baseline_prediction = _predict_value(model_obj, base_inputs)

    scenarios = [
        {
            "name": "Increase sunlight exposure",
            "advice": "Add 20 min/day sunlight and increase exposed skin where safe.",
            "apply": lambda x: {
                **x,
                "Sun_Exposure_min": _bounded_update(x["Sun_Exposure_min"], 20.0, 0.0, 180.0),
                "Skin_Exposure_percent": _bounded_update(x["Skin_Exposure_percent"], 15.0, 0.0, 100.0),
            },
        },
        {
            "name": "Improve diet quality",
            "advice": "Increase fish and dairy frequency by around 3 servings/week each.",
            "apply": lambda x: {
                **x,
                "Fish_intake_week": _bounded_update(x["Fish_intake_week"], 3.0, 0.0, 14.0),
                "Dairy_intake_week": _bounded_update(x["Dairy_intake_week"], 3.0, 0.0, 14.0),
            },
        },
        {
            "name": "Increase activity and reduce indoor time",
            "advice": "Add 2 hours/week activity and reduce indoor work time by 1.5 hours/day.",
            "apply": lambda x: {
                **x,
                "Physical_activity_hours_week": _bounded_update(x["Physical_activity_hours_week"], 2.0, 0.0, 20.0),
                "Indoor_work_hours_day": _bounded_update(x["Indoor_work_hours_day"], -1.5, 0.0, 16.0),
            },
        },
        {
            "name": "Reduce alcohol intake",
            "advice": "Lower weekly alcohol units by 3 where possible.",
            "apply": lambda x: {
                **x,
                "Alcohol_units_week": _bounded_update(x["Alcohol_units_week"], -3.0, 0.0, 30.0),
            },
        },
    ]

    impacts = []
    for scenario in scenarios:
        updated_inputs = scenario["apply"](base_inputs)
        scenario_prediction = _predict_value(model_obj, updated_inputs)
        delta = scenario_prediction - baseline_prediction
        impacts.append(
            {
                "Intervention": scenario["name"],
                "Feature Changes": summarize_feature_changes(base_inputs, updated_inputs),
                "Projected Vitamin D (ng/mL)": round(scenario_prediction, 2),
                "Predicted Change (ng/mL)": round(delta, 2),
                "Projected Status": get_status(scenario_prediction),
                "Advice": scenario["advice"],
            }
        )

    ranked_impacts = sorted(impacts, key=lambda d: d["Predicted Change (ng/mL)"], reverse=True)

    prioritized_plan = []
    for impact in ranked_impacts:
        if impact["Predicted Change (ng/mL)"] > 0:
            prioritized_plan.append(
                f"{impact['Intervention']}: {impact['Advice']} "
                f"Expected gain: +{impact['Predicted Change (ng/mL)']:.2f} ng/mL"
            )

    if not prioritized_plan:
        prioritized_plan.append("No positive intervention signal detected from current scenario set. Maintain current routine and monitor levels.")

    return ranked_impacts, prioritized_plan


def build_gauge(prediction: float) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=prediction,
            number={"suffix": " ng/mL"},
            gauge={
                "axis": {"range": [0, GAUGE_MAX]},
                "bar": {"color": "#b45f2e"},
                "steps": [
                    {"range": [0, DEFICIENT_CUTOFF], "color": "#f8d7bf"},
                    {"range": [DEFICIENT_CUTOFF, INSUFFICIENT_CUTOFF], "color": "#f6c58f"},
                    {"range": [INSUFFICIENT_CUTOFF, GAUGE_MAX], "color": "#e8b07a"},
                ],
            },
        )
    )
    fig.update_traces(number={"font": {"color": "#3b2416"}})
    fig.update_layout(
        paper_bgcolor="#fff2e2",
        plot_bgcolor="#fff2e2",
        font={"color": "#3b2416"},
    )
    fig.update_layout(height=280, margin={"l": 10, "r": 10, "t": 30, "b": 10})
    return fig


st.title("Vitamin D AI Prediction System")


if not MODEL_PATH.exists():
    st.error(
        "Model file 'advanced_model.pkl' was not found in deploy_app. "
        "Add the file and redeploy."
    )
    st.stop()

model = load_model(MODEL_PATH)

with st.container(border=True):
    mode = st.radio("Input Mode", ["Basic", "Advanced"], horizontal=True)

    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", min_value=1, max_value=100, value=25, step=1)
        weight_kg = st.number_input("Weight (kg)", min_value=20.0, max_value=220.0, value=70.0, step=0.5)
        bmi = st.number_input("BMI", min_value=10.0, max_value=60.0, value=24.0, step=0.1)
    with col2:
        height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=230.0, value=170.0, step=0.5)
        sun_exposure = st.slider("Sun Exposure (min/day)", min_value=0, max_value=180, value=30, step=5)
        physical_activity = st.slider("Physical Activity (hours/week)", min_value=0.0, max_value=20.0, value=3.0, step=0.5)

    gender_map = {"Female": 0, "Male": 1}

    if mode == "Advanced":
        adv1, adv2 = st.columns(2)
        with adv1:
            gender = st.selectbox("Gender", list(gender_map.keys()), index=1)
            body_fat = st.number_input("Body Fat %", min_value=5.0, max_value=60.0, value=22.0, step=0.1)
            skin_exposure = st.slider("Skin Exposure %", min_value=0, max_value=100, value=40, step=5)
            fish_intake = st.slider("Fish intake/week", min_value=0, max_value=14, value=2, step=1)
        with adv2:
            dairy_intake = st.slider("Dairy intake/week", min_value=0, max_value=14, value=4, step=1)
            alcohol_units = st.slider("Alcohol units/week", min_value=0, max_value=30, value=0, step=1)
            indoor_work = st.slider("Indoor work hours/day", min_value=0.0, max_value=16.0, value=7.0, step=0.5)
    else:
        gender = "Male"
        body_fat = 22.0
        skin_exposure = 40
        fish_intake = 2
        dairy_intake = 4
        alcohol_units = 0
        indoor_work = 7.0

    predict_clicked = st.button("Predict Vitamin D Level", use_container_width=True, type="primary")


if predict_clicked:
    model_input = {
        "Age": float(age),
        "Gender": float(gender_map[gender]),
        "Weight_kg": float(weight_kg),
        "Height_cm": float(height_cm),
        "BMI": float(bmi),
        "BodyFat_percent": float(body_fat),
        "Sun_Exposure_min": float(sun_exposure),
        "Skin_Exposure_percent": float(skin_exposure),
        "Fish_intake_week": float(fish_intake),
        "Dairy_intake_week": float(dairy_intake),
        "Alcohol_units_week": float(alcohol_units),
        "Physical_activity_hours_week": float(physical_activity),
        "Indoor_work_hours_day": float(indoor_work),
    }

    input_df = build_prediction_input(model_input)
    prediction = float(model.predict(input_df)[0])
    status = get_status(prediction)

    st.subheader("Prediction Output")
    left_metric, right_metric = st.columns(2)
    left_metric.metric("Predicted Vitamin D Level", f"{prediction:.2f} ng/mL")
    right_metric.metric("Status", status)

    progress_value = min(max(prediction / GAUGE_MAX, 0.0), 1.0)
    st.progress(progress_value, text="Prediction scale")
    st.plotly_chart(build_gauge(prediction), use_container_width=True, config={"displayModeBar": False})

    st.subheader("Interpretation")
    st.caption("Model interpretation of your input profile.")
    for reason in explain_prediction(model_input):
        st.write(f"- {reason}")

    st.write("Interpretation Table (What If Sun or Diet Is Increased)")
    interpretation_df = build_interpretation_table(model, model_input)
    st.dataframe(interpretation_df, use_container_width=True, hide_index=True)

    st.subheader("AI Recommendations")
    for tip in build_recommendations(model_input):
        st.write(f"- {tip}")

    st.subheader("Intervention Impact (What If You Change Sun, Diet, Activity)")
    st.caption("This table estimates how your Vitamin D level may change if you increase sun exposure, improve diet, or adjust lifestyle factors.")

    ranked_impacts, prioritized_plan = generate_agentic_recommendations(model, model_input)
    ranked_df = pd.DataFrame(ranked_impacts)
    st.dataframe(
        ranked_df[["Intervention", "Feature Changes", "Projected Vitamin D (ng/mL)", "Predicted Change (ng/mL)", "Projected Status"]],
        use_container_width=True,
        hide_index=True,
    )

    st.write("Top priority actions")
    for action in prioritized_plan[:3]:
        st.write(f"- {action}")

st.warning("This is for educational purposes only")
