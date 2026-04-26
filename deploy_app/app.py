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
    page_title="Vitamin D AI Prediction System",
    page_icon="D",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        --bg: #f7f7fb;
        --panel: #ffffff;
        --border: #e7e8ef;
        --text: #111827;
        --muted: #6b7280;
        --primary: #2563eb;
        --primary-strong: #1d4ed8;
    }
    .stApp {
        background: radial-gradient(circle at top right, #eef4ff 0%, #f7f7fb 45%, #f7f7fb 100%);
        color: var(--text);
    }
    .block-container {
        max-width: 1180px;
        padding-top: 1.1rem;
        padding-bottom: 2.2rem;
    }
    .panel {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1rem 1rem 1.1rem 1rem;
        box-shadow: 0 10px 30px rgba(17, 24, 39, 0.06);
        margin-bottom: 0.8rem;
    }
    .section-title {
        font-size: 0.92rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        color: #374151;
        text-transform: uppercase;
        margin: 0.4rem 0 0.5rem 0;
    }
    .result-value {
        font-size: 2.15rem;
        font-weight: 800;
        color: var(--text);
        line-height: 1.15;
        margin-top: 0.2rem;
        margin-bottom: 0.35rem;
    }
    .status-chip {
        display: inline-block;
        padding: 0.32rem 0.68rem;
        border-radius: 999px;
        border: 1px solid #dbe6ff;
        background: #eff6ff;
        color: #1e40af;
        font-weight: 600;
        font-size: 0.88rem;
        margin-bottom: 0.75rem;
    }
    .mode-label {
        color: var(--muted);
        font-size: 0.92rem;
        margin-top: -0.2rem;
        margin-bottom: 0.6rem;
    }
    .stButton > button {
        min-height: 3rem;
        border-radius: 12px;
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-strong) 100%);
        border: 1px solid var(--primary-strong);
        color: #ffffff;
        font-weight: 700;
        font-size: 1rem;
    }
    .stButton > button:hover {
        filter: brightness(1.03);
    }
    [data-testid="stMetric"] {
        background: #f8faff;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.7rem;
    }
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
    }
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.75rem;
            padding-right: 0.75rem;
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
    fig.update_layout(height=280, margin={"l": 10, "r": 10, "t": 30, "b": 10})
    return fig


st.title("Vitamin D AI Prediction System")
st.caption("Clean, two-panel experience for quick screening or detailed analysis.")

if not MODEL_PATH.exists():
    st.error(
        "Model file 'advanced_model.pkl' was not found in deploy_app. "
        "Add the file and redeploy."
    )
    st.stop()

model = load_model(MODEL_PATH)

left_panel, right_panel = st.columns([1, 1], gap="large")

with left_panel:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    mode = st.radio(
        "Input Mode",
        ["Quick Mode (Basic)", "Detailed Mode (Advanced)"],
        horizontal=True,
    )

    if mode == "Quick Mode (Basic)":
        st.markdown('<div class="mode-label">⚡ Quick Estimate (faster, less accurate)</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="mode-label">🧠 Detailed Analysis (more accurate)</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Personal Info</div>', unsafe_allow_html=True)
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        age = st.number_input("Age", min_value=1, max_value=100, value=25, step=1)
    with p_col2:
        bmi = st.number_input("BMI", min_value=10.0, max_value=60.0, value=24.0, step=0.1)

    gender_map = {"Female": 0, "Male": 1}
    gender = "Male"
    body_fat = 22.0
    skin_exposure = 40
    fish_intake = 2
    dairy_intake = 4
    alcohol_units = 0
    indoor_work = 7.0

    if mode == "Detailed Mode (Advanced)":
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            gender = st.selectbox("Gender", list(gender_map.keys()), index=1)
        with d_col2:
            body_fat = st.number_input("Body Fat %", min_value=5.0, max_value=60.0, value=22.0, step=0.1)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Lifestyle</div>', unsafe_allow_html=True)
    l_col1, l_col2 = st.columns(2)
    with l_col1:
        sun_exposure = st.slider("Sun Exposure (min/day)", min_value=0, max_value=180, value=30, step=5)
    with l_col2:
        physical_activity = st.slider("Physical Activity (hours/week)", min_value=0.0, max_value=20.0, value=3.0, step=0.5)

    if mode == "Detailed Mode (Advanced)":
        l2_col1, l2_col2 = st.columns(2)
        with l2_col1:
            skin_exposure = st.slider("Skin Exposure %", min_value=0, max_value=100, value=40, step=5)
        with l2_col2:
            indoor_work = st.slider("Indoor work hours/day", min_value=0.0, max_value=16.0, value=7.0, step=0.5)

    if mode == "Detailed Mode (Advanced)":
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Diet</div>', unsafe_allow_html=True)
        diet_col1, diet_col2 = st.columns(2)
        with diet_col1:
            fish_intake = st.slider("Fish intake/week", min_value=0, max_value=14, value=2, step=1)
            alcohol_units = st.slider("Alcohol units/week", min_value=0, max_value=30, value=0, step=1)
        with diet_col2:
            dairy_intake = st.slider("Dairy intake/week", min_value=0, max_value=14, value=4, step=1)

    st.markdown("<br>", unsafe_allow_html=True)
    btn_left, btn_mid, btn_right = st.columns([1, 2.2, 1])
    with btn_mid:
        predict_clicked = st.button("Predict Vitamin D", use_container_width=True, type="primary")

    st.markdown("</div>", unsafe_allow_html=True)

if predict_clicked:
    model_input = {
        "Age": float(age),
        "Gender": float(gender_map[gender]),
        "Weight_kg": 70.0,
        "Height_cm": 170.0,
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
    st.session_state["last_model_input"] = model_input
    st.session_state["last_mode"] = mode

with right_panel:
    if "last_model_input" in st.session_state:
        model_input = st.session_state["last_model_input"]
        active_mode = st.session_state.get("last_mode", "Quick Mode (Basic)")

        input_df = build_prediction_input(model_input)
        prediction = float(model.predict(input_df)[0])
        status = get_status(prediction)

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("Prediction Output")
        st.markdown(f'<div class="result-value">{prediction:.2f} ng/mL</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="status-chip">Status: {status}</div>', unsafe_allow_html=True)

        progress_value = min(max(prediction / GAUGE_MAX, 0.0), 1.0)
        st.progress(progress_value, text="Prediction scale")
        st.plotly_chart(build_gauge(prediction), use_container_width=True, config={"displayModeBar": False})

        if active_mode == "Detailed Mode (Advanced)":
            st.subheader("Why this prediction?")
            for reason in explain_prediction(model_input):
                st.write(f"- {reason}")

            st.subheader("AI Recommendations")
            for tip in build_recommendations(model_input):
                st.write(f"- {tip}")

            st.subheader("Interpretation Table (What If Sun or Diet Is Increased)")
            interpretation_df = build_interpretation_table(model, model_input)
            st.dataframe(interpretation_df, use_container_width=True, hide_index=True)

            st.subheader("Chatbot")
            st.info("Chatbot is not available in this deployment yet.")

        st.markdown("</div>", unsafe_allow_html=True)

st.warning("This is for educational purposes only")
