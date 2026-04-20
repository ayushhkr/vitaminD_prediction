from pathlib import Path

import joblib
import pandas as pd
import streamlit as st


MODEL_PATH = Path(__file__).resolve().parent / "best_model.joblib"
DEFICIENCY_THRESHOLD = 20.0

model = joblib.load(MODEL_PATH)

st.set_page_config(page_title="Vitamin D Predictor", page_icon="☀️")
st.title("Vitamin D Predictor")
st.write("Enter a few lifestyle and body features to estimate Vitamin D level.")
st.caption("This app uses the lightweight saved pipeline model for deployment.")

age = st.number_input("Age", min_value=0, max_value=100, value=25)
gender = st.selectbox("Gender", [0, 1], format_func=lambda x: "Female" if x == 0 else "Male")
weight = st.number_input("Weight (kg)", min_value=20.0, max_value=200.0, value=72.0)
height = st.number_input("Height (cm)", min_value=100.0, max_value=220.0, value=170.0)
bmi = st.number_input("BMI", min_value=10.0, max_value=60.0, value=24.0)
bodyfat = st.number_input("Body Fat %", min_value=1.0, max_value=70.0, value=18.0)
sun = st.number_input("Sun Exposure (min/day)", min_value=0.0, max_value=300.0, value=25.0)
skin = st.number_input("Skin Exposure %", min_value=0.0, max_value=100.0, value=40.0)
fish = st.number_input("Fish intake/week", min_value=0.0, max_value=21.0, value=1.0)
dairy = st.number_input("Dairy intake/week", min_value=0.0, max_value=21.0, value=5.0)
alcohol = st.number_input("Alcohol units/week", min_value=0.0, max_value=40.0, value=0.0)
activity = st.number_input("Physical activity (hrs/week)", min_value=0.0, max_value=40.0, value=3.0)
indoor = st.number_input("Indoor work hrs/day", min_value=0.0, max_value=24.0, value=6.0)

input_df = pd.DataFrame(
    [[
        age,
        gender,
        weight,
        height,
        bmi,
        bodyfat,
        sun,
        skin,
        alcohol,
        fish,
        dairy,
        activity,
        indoor,
    ]],
    columns=[
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
    ],
)

if st.button("Predict"):
    prediction = float(model.predict(input_df)[0])
    status = "Deficient" if prediction < DEFICIENCY_THRESHOLD else "Not Deficient"
    st.success(f"Predicted Vitamin D Level: {prediction:.2f} ng/mL")
    st.info(f"Deficiency Status: {status}")
