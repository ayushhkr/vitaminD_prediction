import streamlit as st
from app_modules.chatbot import init_chat_state, render_chat_widget
from app_modules.constants import GAUGE_MAX, LAYOUT, MODEL_PATH, PAGE_ICON, PAGE_TITLE
from app_modules.interpretation import render_interpretation_insights
from app_modules.prediction import (
    build_gauge,
    build_interpretation_table,
    build_prediction_input,
    build_recommendations,
    explain_prediction,
    get_status,
    load_model,
)
from app_modules.styles import apply_global_styles


st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=LAYOUT)
apply_global_styles()

QUICK_MODE = "⚡ Quick Estimate"
DETAILED_MODE = "🧠 Detailed Analysis"


def normalize_mode_label(mode_label: str) -> str:
    if mode_label in {DETAILED_MODE, "Detailed Mode (Advanced)"}:
        return DETAILED_MODE
    return QUICK_MODE


def render_input_panel() -> tuple[bool, dict, str]:
    defaults = st.session_state.get("last_model_input", {})
    default_mode = normalize_mode_label(st.session_state.get("last_mode", QUICK_MODE))

    def _clamp(value, min_value, max_value):
        return max(min_value, min(max_value, value))

    with st.container():
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        mode = st.radio(
            "Input Mode",
            [QUICK_MODE, DETAILED_MODE],
            index=0 if default_mode == QUICK_MODE else 1,
            horizontal=True,
        )

        if mode == QUICK_MODE:
            st.markdown(
                '<div class="mode-label">Fast screening using core inputs only.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="mode-label">Richer profile inputs for better context and recommendations.</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="section-title">🟢 Personal Info</div>', unsafe_allow_html=True)
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            age = st.number_input(
                "Age",
                min_value=1,
                max_value=100,
                value=int(_clamp(float(defaults.get("Age", 25)), 1, 100)),
                step=1,
            )
        with p_col2:
            bmi = st.number_input(
                "BMI",
                min_value=10.0,
                max_value=60.0,
                value=float(_clamp(float(defaults.get("BMI", 24.0)), 10.0, 60.0)),
                step=0.1,
            )

        gender_map = {"Female": 0, "Male": 1}
        gender = "Male" if float(defaults.get("Gender", 1.0)) >= 0.5 else "Female"
        body_fat = float(_clamp(float(defaults.get("BodyFat_percent", 22.0)), 5.0, 60.0))
        skin_exposure = int(_clamp(float(defaults.get("Skin_Exposure_percent", 40)), 0, 100))
        fish_intake = int(_clamp(float(defaults.get("Fish_intake_week", 2)), 0, 14))
        dairy_intake = int(_clamp(float(defaults.get("Dairy_intake_week", 4)), 0, 14))
        alcohol_units = int(_clamp(float(defaults.get("Alcohol_units_week", 0)), 0, 30))
        indoor_work = float(_clamp(float(defaults.get("Indoor_work_hours_day", 7.0)), 0.0, 16.0))

        if mode == DETAILED_MODE:
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                gender = st.selectbox("Gender", list(gender_map.keys()), index=1 if gender == "Male" else 0)
            with d_col2:
                body_fat = st.number_input("Body Fat %", min_value=5.0, max_value=60.0, value=body_fat, step=0.1)

        st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🟡 Lifestyle</div>', unsafe_allow_html=True)
        l_col1, l_col2 = st.columns(2)
        with l_col1:
            sun_exposure = st.slider(
                "Sun Exposure (min/day)",
                min_value=0,
                max_value=180,
                value=int(_clamp(float(defaults.get("Sun_Exposure_min", 30)), 0, 180)),
                step=5,
            )
        with l_col2:
            physical_activity = st.slider(
                "Physical Activity (hours/week)",
                min_value=0.0,
                max_value=20.0,
                value=float(_clamp(float(defaults.get("Physical_activity_hours_week", 3.0)), 0.0, 20.0)),
                step=0.5,
            )

        if mode == DETAILED_MODE:
            l2_col1, l2_col2 = st.columns(2)
            with l2_col1:
                skin_exposure = st.slider("Skin Exposure %", min_value=0, max_value=100, value=skin_exposure, step=5)
            with l2_col2:
                indoor_work = st.slider("Indoor work hours/day", min_value=0.0, max_value=16.0, value=indoor_work, step=0.5)

        if mode == DETAILED_MODE:
            st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🟠 Diet</div>', unsafe_allow_html=True)
            diet_col1, diet_col2 = st.columns(2)
            with diet_col1:
                fish_intake = st.slider("Fish intake/week", min_value=0, max_value=14, value=fish_intake, step=1)
                alcohol_units = st.slider("Alcohol units/week", min_value=0, max_value=30, value=alcohol_units, step=1)
            with diet_col2:
                dairy_intake = st.slider("Dairy intake/week", min_value=0, max_value=14, value=dairy_intake, step=1)

        st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
        _, btn_mid, _ = st.columns([1, 2.2, 1])
        with btn_mid:
            predict_clicked = st.button("Predict Vitamin D", use_container_width=True, type="primary")

        st.markdown("</div>", unsafe_allow_html=True)

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
    return predict_clicked, model_input, mode


def render_output_panel(model, model_input: dict, active_mode: str) -> None:
    input_df = build_prediction_input(model_input)
    prediction = float(model.predict(input_df)[0])
    status = get_status(prediction)
    status_class_map = {
        "Deficient": "status-chip status-deficient",
        "Insufficient": "status-chip status-insufficient",
        "Sufficient": "status-chip status-sufficient",
    }
    status_class = status_class_map.get(status, "status-chip")

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("🔵 Prediction Output")
    summary_col, gauge_col = st.columns([2, 1], gap="medium")

    with summary_col:
        st.markdown(f'<div class="result-value">{prediction:.2f} ng/mL</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="{status_class}">Status: {status}</div>', unsafe_allow_html=True)
        progress_value = min(max(prediction / GAUGE_MAX, 0.0), 1.0)
        st.progress(progress_value)
        st.caption("Prediction scale")

    with gauge_col:
        st.plotly_chart(build_gauge(prediction), use_container_width=True, config={"displayModeBar": False})

    if active_mode == DETAILED_MODE:
        st.divider()
        st.subheader("🧠 Why this?")
        reasons = explain_prediction(model_input)
        st.markdown("\n".join(f"- {reason}" for reason in reasons))

        st.divider()
        st.subheader("🤖 AI Recommendations")
        tips = []
        if status == "Deficient":
            tips.append("Your predicted level is low; prioritize daily sunlight and nutrition changes consistently for the next 8-12 weeks.")
        elif status == "Insufficient":
            tips.append("You are close to a sufficient range; a modest increase in sun exposure and diet quality can improve levels.")
        else:
            tips.append("Your predicted level is in a healthy range; maintain your current routine and monitor periodically.")

        for suggestion in build_recommendations(model_input):
            if suggestion not in tips:
                tips.append(suggestion)
            if len(tips) >= 3:
                break

        while len(tips) < 3:
            tips.append("Track your habits weekly so improvements in sunlight, diet, and activity stay consistent.")

        st.markdown("\n".join(f"- {tip}" for tip in tips))

        st.divider()
        st.subheader("📊 What-If Analysis")
        interpretation_df = build_interpretation_table(model, model_input)
        render_interpretation_insights(interpretation_df)

        init_chat_state()
        render_chat_widget(model_input, prediction, status)

    st.markdown("</div>", unsafe_allow_html=True)


st.title(PAGE_TITLE)
st.caption("Clean, two-panel experience for quick screening or detailed analysis.")

if not MODEL_PATH.exists():
    st.error("Model file 'advanced_model.pkl' was not found in deploy_app_advanced. Add the file and redeploy.")
    st.stop()

model = load_model(MODEL_PATH)

has_prediction = "last_model_input" in st.session_state

if has_prediction:
    with st.sidebar:
        st.subheader("Input Form")
        st.caption("Update values and click Predict Vitamin D to refresh results.")
        st.divider()
        predict_clicked, model_input, mode = render_input_panel()

    if predict_clicked:
        st.session_state["last_model_input"] = model_input
        st.session_state["last_mode"] = mode

    render_output_panel(
        model,
        st.session_state["last_model_input"],
        normalize_mode_label(st.session_state.get("last_mode", QUICK_MODE)),
    )
else:
    left_panel, right_panel = st.columns([1, 1], gap="medium")

    with left_panel:
        predict_clicked, model_input, mode = render_input_panel()

    if predict_clicked:
        st.session_state["last_model_input"] = model_input
        st.session_state["last_mode"] = mode

    with right_panel:
        if "last_model_input" in st.session_state:
            render_output_panel(
                model,
                st.session_state["last_model_input"],
                normalize_mode_label(st.session_state.get("last_mode", QUICK_MODE)),
            )
