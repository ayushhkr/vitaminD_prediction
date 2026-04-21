from pathlib import Path

import joblib
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


MODEL_PATH = Path(__file__).resolve().parent / "best_model.joblib"
DEFICIENCY_THRESHOLD = 20.0
INSUFFICIENCY_THRESHOLD = 30.0

model = joblib.load(MODEL_PATH)

st.set_page_config(
    page_title="Vitamin D Predictor",
    page_icon="VD",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        --space-1: 0.5rem;
        --space-2: 0.8rem;
        --space-3: 1.1rem;
        --space-4: 1.5rem;
        --space-5: 2rem;
        --sand-50: #fffdf8;
        --sand-100: #fff7ea;
        --sand-200: #fdeccf;
        --sun-300: #f6c66a;
        --sun-500: #e89c2a;
        --sun-700: #ad6408;
        --ink-900: #22160e;
        --ink-700: #533526;
        --header-bg: rgba(255, 248, 236, 0.92);
        --mint-100: #dbf4e2;
        --mint-700: #146c43;
        --rose-100: #fde4e4;
        --rose-700: #9f2c2c;
    }
    * {
        font-family: "Segoe UI", "Trebuchet MS", "Gill Sans", sans-serif;
    }
    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(232, 156, 42, 0.22), transparent 34%),
            radial-gradient(circle at 88% 6%, rgba(44, 142, 127, 0.2), transparent 30%),
            linear-gradient(180deg, var(--sand-50) 0%, var(--sand-100) 48%, #fdf1dd 100%);
        color: var(--ink-900);
        overflow-x: hidden;
    }
    .block-container {
        padding-top: var(--space-4);
        padding-bottom: var(--space-5);
        padding-left: var(--space-3);
        padding-right: var(--space-3);
        max-width: 1200px;
    }
    header[data-testid="stHeader"] {
        background: var(--header-bg);
        backdrop-filter: blur(6px);
        border-bottom: 1px solid rgba(173, 100, 8, 0.2);
    }
    [data-testid="stToolbar"] button,
    [data-testid="stHeader"] button,
    [data-testid="stHeader"] a,
    [data-testid="stHeader"] p,
    [data-testid="stHeader"] span {
        color: var(--ink-900) !important;
    }
    [data-testid="stHeader"] svg {
        fill: var(--ink-900) !important;
        color: var(--ink-900) !important;
    }
    h1, h2, h3 {
        color: var(--ink-900);
        font-weight: 800;
        letter-spacing: -0.02em;
    }
    p {
        color: var(--ink-700);
    }
    [data-testid="stCaptionContainer"] p {
        color: var(--ink-900) !important;
        font-weight: 600;
        opacity: 1 !important;
    }
    .hero-card, .section-card, .insight-card {
        background: rgba(255, 255, 255, 0.94);
        border: 1px solid rgba(173, 100, 8, 0.18);
        border-radius: 24px;
        padding: var(--space-4);
        box-shadow: 0 14px 34px rgba(83, 53, 38, 0.12);
        margin-bottom: var(--space-3);
        display: flex;
        flex-direction: column;
        gap: var(--space-1);
    }
    .hero-title {
        font-size: 2.1rem;
        line-height: 1.05;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #6c2f08;
        margin-bottom: 0.45rem;
    }
    .hero-text {
        font-size: 0.95rem;
        color: var(--ink-700);
        margin-bottom: 0;
    }
    .eyebrow {
        text-transform: uppercase;
        letter-spacing: 0.16em;
        font-size: 0.76rem;
        font-weight: 700;
        color: var(--sun-700);
        margin-bottom: 0.7rem;
    }
    .metric-strip {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: var(--space-2);
        margin-top: var(--space-2);
    }
    .mini-stat {
        border-radius: 18px;
        padding: 0.95rem 1rem;
        background: linear-gradient(135deg, #fff7e0 0%, #ffe7ba 100%);
        border: 1px solid rgba(173, 100, 8, 0.18);
    }
    .mini-label {
        font-size: 0.78rem;
        color: #4a2f19;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.28rem;
    }
    .mini-value {
        font-size: 1.2rem;
        font-weight: 800;
        color: #61280a;
    }
    .status-pill {
        display: inline-block;
        padding: 0.42rem 0.8rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.9rem;
        margin-top: 0.35rem;
    }
    .status-deficient {
        background: var(--rose-100);
        color: var(--rose-700);
    }
    .status-insufficient {
        background: #fff0c8;
        color: #84510c;
    }
    .status-sufficient {
        background: var(--mint-100);
        color: var(--mint-700);
    }
    .section-title {
        font-size: 1.02rem;
        font-weight: 800;
        color: var(--ink-900);
        border-left: 4px solid var(--sun-500);
        padding-left: 0.55rem;
        margin-top: 0.1rem;
        margin-bottom: 0.35rem;
    }
    .section-text {
        font-size: 0.86rem;
        line-height: 1.4;
        color: var(--ink-700);
        margin-bottom: var(--space-2);
    }
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(173, 100, 8, 0.2);
        border-radius: 20px;
        padding: 1rem 1.05rem;
        box-shadow: 0 10px 28px rgba(83, 53, 38, 0.09);
    }
    div[data-testid="stMetric"] > div {
        gap: 0.2rem;
    }
    div[data-testid="stMetricLabel"] {
        color: var(--sun-700);
        font-weight: 700;
        font-size: 0.8rem;
        line-height: 1.25;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
    }
    div[data-testid="stMetricValue"] {
        color: var(--ink-900);
        font-size: 1.45rem;
        line-height: 1.2;
        white-space: normal !important;
    }
    div[data-testid="stForm"] {
        border: 1px solid rgba(173, 100, 8, 0.15);
        border-radius: 18px;
        padding: var(--space-3);
        background: rgba(255, 255, 255, 0.88);
        margin-top: var(--space-1);
        margin-bottom: var(--space-2);
    }
    div[data-testid="stForm"] [data-testid="column"] {
        padding-right: 0.25rem;
    }
    div[data-testid="stForm"] .stNumberInput,
    div[data-testid="stForm"] .stSelectbox,
    div[data-testid="stForm"] .stSlider {
        margin-bottom: 0.15rem;
    }
    div[data-testid="stForm"] button[kind="formSubmit"] {
        margin-top: var(--space-2);
        width: 100%;
    }
    div[data-testid="stForm"] div[data-testid="stHorizontalBlock"] {
        align-items: flex-start;
        gap: var(--space-3);
    }
    div[data-testid="stPlotlyChart"] {
        margin-top: var(--space-1);
        margin-bottom: var(--space-2);
    }
    @media (max-width: 900px) {
        .block-container {
            padding-left: var(--space-2);
            padding-right: var(--space-2);
            padding-top: var(--space-3);
            padding-bottom: var(--space-4);
        }
        div[data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: var(--space-2) !important;
        }
        div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
        .hero-title {
            font-size: 1.75rem;
            line-height: 1.12;
        }
        .metric-strip {
            grid-template-columns: 1fr;
        }
        .hero-card, .section-card, .insight-card {
            padding: var(--space-3);
            border-radius: 18px;
        }
        .section-title {
            font-size: 0.96rem;
        }
        .section-text {
            font-size: 0.82rem;
        }
        div[data-testid="stMetric"] {
            padding: 0.85rem 0.9rem;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.25rem;
        }
        div[data-testid="stForm"] {
            padding: 0.9rem;
        }
        div[data-testid="stForm"] button[kind="formSubmit"] {
            min-height: 2.7rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def build_input_frame(values: dict[str, float | int]) -> pd.DataFrame:
    """Create the model input frame in the expected column order."""
    return pd.DataFrame([values])[
        [
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
    ]


def vitamin_d_band(value: float) -> tuple[str, str]:
    """Map prediction to a simple clinical-style band."""
    if value < DEFICIENCY_THRESHOLD:
        return "Deficient", "status-deficient"
    if value < INSUFFICIENCY_THRESHOLD:
        return "Insufficient", "status-insufficient"
    return "Sufficient", "status-sufficient"


def build_gauge(prediction: float) -> go.Figure:
    """Create a gauge chart for the predicted Vitamin D level."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=prediction,
            number={"suffix": " ng/mL", "font": {"size": 34, "color": "#7c2d12"}},
            gauge={
                "axis": {"range": [0, 60], "tickwidth": 1, "tickcolor": "#7c2d12"},
                "bar": {"color": "#f59e0b"},
                "bgcolor": "white",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, DEFICIENCY_THRESHOLD], "color": "#fecaca"},
                    {"range": [DEFICIENCY_THRESHOLD, INSUFFICIENCY_THRESHOLD], "color": "#fde68a"},
                    {"range": [INSUFFICIENCY_THRESHOLD, 60], "color": "#bbf7d0"},
                ],
                "threshold": {
                    "line": {"color": "#7c2d12", "width": 4},
                    "thickness": 0.8,
                    "value": DEFICIENCY_THRESHOLD,
                },
            },
        )
    )
    fig.update_layout(
        title={
            "text": "Predicted Vitamin D Level",
            "x": 0.02,
            "xanchor": "left",
            "y": 0.98,
            "yanchor": "top",
            "font": {"size": 16, "color": "#6c2f08"},
        },
        font={"color": "#3b2417"},
        margin={"l": 10, "r": 10, "t": 68, "b": 18},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=280,
    )
    return fig


left, right = st.columns([1.15, 0.85], gap="large")

with left:
    st.markdown(
        """
        <div class="hero-card">
            <div class="eyebrow">Screening Demo</div>
            <div class="hero-title">Vitamin D Predictor</div>
            <p class="hero-text">
                A cleaner, deployment-ready interface for estimating Vitamin D level from
                body composition, sunlight, diet, and activity signals.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        """
        <div class="hero-card">
            <div class="section-title">How To Read The Result</div>
            <p class="section-text">
                The app predicts Vitamin D in ng/mL and groups the result into a simple
                status band for quick interpretation.
            </p>
            <div class="metric-strip">
                <div class="mini-stat">
                    <div class="mini-label">Deficient</div>
                    <div class="mini-value">&lt; 20</div>
                </div>
                <div class="mini-stat">
                    <div class="mini-label">Insufficient</div>
                    <div class="mini-value">20 - 29.9</div>
                </div>
                <div class="mini-stat">
                    <div class="mini-label">Sufficient</div>
                    <div class="mini-value">30+</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

input_col, results_col = st.columns([0.95, 1.05], gap="large")

with input_col:
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">Input Profile</div>
            <p class="section-text">
                Fill in the person-level inputs below. The layout is grouped so it feels closer
                to a lightweight clinical screening form.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("prediction_form", clear_on_submit=False):
        demo_a, demo_b = st.columns(2)
        with demo_a:
            age = st.number_input("Age", min_value=0, max_value=100, value=25)
            gender = st.selectbox("Gender", [0, 1], format_func=lambda x: "Female" if x == 0 else "Male")
            weight = st.number_input("Weight (kg)", min_value=20.0, max_value=200.0, value=72.0, step=0.5)
            height = st.number_input("Height (cm)", min_value=100.0, max_value=220.0, value=170.0, step=0.5)
        with demo_b:
            bmi = st.number_input("BMI", min_value=10.0, max_value=60.0, value=24.0, step=0.1)
            bodyfat = st.number_input("Body Fat %", min_value=1.0, max_value=70.0, value=18.0, step=0.1)
            indoor = st.number_input("Indoor work (hrs/day)", min_value=0.0, max_value=24.0, value=6.0, step=0.5)
            activity = st.number_input("Physical activity (hrs/week)", min_value=0.0, max_value=40.0, value=3.0, step=0.5)

        lifestyle_a, lifestyle_b = st.columns(2)
        with lifestyle_a:
            sun = st.slider("Sun Exposure (min/day)", min_value=0, max_value=300, value=25, step=5)
            skin = st.slider("Skin Exposure (%)", min_value=0, max_value=100, value=40, step=5)
            fish = st.slider("Fish intake/week", min_value=0, max_value=14, value=1)
        with lifestyle_b:
            dairy = st.slider("Dairy intake/week", min_value=0, max_value=14, value=5)
            alcohol = st.slider("Alcohol units/week", min_value=0, max_value=40, value=0)

        submitted = st.form_submit_button("Predict Vitamin D")

    calculated_bmi = round(weight / ((height / 100) ** 2), 1) if height > 0 else 0.0
    bmi_gap = round(abs(calculated_bmi - bmi), 1)
    st.caption(
        f"Calculated BMI from weight and height: {calculated_bmi}. "
        f"Current BMI input differs by {bmi_gap}."
    )

    input_values = {
        "Age": age,
        "Gender": gender,
        "Weight_kg": weight,
        "Height_cm": height,
        "BMI": bmi,
        "BodyFat_percent": bodyfat,
        "Sun_Exposure_min": sun,
        "Skin_Exposure_percent": skin,
        "Alcohol_units_week": alcohol,
        "Fish_intake_week": fish,
        "Dairy_intake_week": dairy,
        "Physical_activity_hours_week": activity,
        "Indoor_work_hours_day": indoor,
    }

with results_col:
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">Prediction Dashboard</div>
            <p class="section-text">
                Generate a result to view the estimated Vitamin D level and status band.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if submitted:
        input_df = build_input_frame(input_values)
        prediction = float(model.predict(input_df)[0])
        status_label, status_class = vitamin_d_band(prediction)

        metric_a, metric_b, metric_c = st.columns(3)
        metric_a.metric("Predicted Vitamin D", f"{prediction:.2f} ng/mL")
        metric_b.metric("Status Band", status_label)
        metric_c.metric("Deficiency Cutoff", f"{DEFICIENCY_THRESHOLD:.0f} ng/mL")

        st.markdown(
            f'<span class="status-pill {status_class}">{status_label}</span>',
            unsafe_allow_html=True,
        )

        st.caption("Chart: Prediction Gauge")
        st.plotly_chart(build_gauge(prediction), use_container_width=True, config={"displayModeBar": False})

        insight_cols = st.columns(2)
        with insight_cols[0]:
            st.markdown(
                """
                <div class="insight-card">
                    <div class="section-title">Quick Interpretation</div>
                    <p class="section-text">
                        Lower sun exposure, lower diet diversity, and high indoor time can all push
                        Vitamin D prediction downward in this simplified model.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with insight_cols[1]:
            st.markdown(
                """
                <div class="insight-card">
                    <div class="section-title">Model Note</div>
                    <p class="section-text">
                        This prediction is for educational screening use only. It should not replace
                        laboratory testing or clinical judgment.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("Fill in the profile and click 'Predict Vitamin D' to see the dashboard.")
