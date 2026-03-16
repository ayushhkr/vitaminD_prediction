# Non-Invasive Prediction of Vitamin D Deficiency Using Machine Learning

## Project Overview

Vitamin D deficiency is a widespread health issue that can lead to bone disorders, weakened immunity, and other health complications. Traditional diagnosis requires blood tests, which are invasive and costly.

This project proposes a **machine learning-based non-invasive method** to estimate Vitamin D levels using lifestyle and physiological parameters.

The system predicts Vitamin D levels using factors such as:

- Age
- BMI
- Sun exposure
- Skin exposure
- Diet (fish and dairy intake)
- Physical activity
- Indoor working hours
- Body fat percentage

---

## Dataset

The dataset contains **10,000 samples** with **17 features** related to lifestyle and physiological parameters affecting Vitamin D levels.

Features include:

- Age
- Gender
- BMI
- Body fat percentage
- Sun exposure duration
- Skin exposure percentage
- Sunscreen usage
- Fish intake per week
- Dairy intake per week
- Alcohol consumption
- Physical activity hours
- Indoor working hours
- Skin tone

Target variable:

- VitaminD_Level_ng_ml

---

## Machine Learning Pipeline

The project follows a complete machine learning workflow:

1. Data Loading
2. Exploratory Data Analysis (EDA)
3. Data Preprocessing
4. Feature Selection
5. Model Training
6. Model Evaluation
7. Feature Importance Analysis
8. Prediction System

---

## Models Used

The following regression models were implemented:

- Linear Regression
- Random Forest Regressor

---

## Model Evaluation Metrics

Model performance was evaluated using:

- R² Score
- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)

Example results:

| Model             | R² Score        |
| ----------------- | --------------- |
| Linear Regression | ~0.78           |
| Random Forest     | Higher accuracy |

---

## Feature Importance

Feature importance analysis revealed that **sun exposure duration** is the most significant factor influencing Vitamin D levels, followed by:

- Body fat percentage
- Skin exposure
- Fish intake
- Physical activity

This aligns with biological understanding that Vitamin D synthesis primarily occurs in the skin through sunlight exposure.

---

## Example Prediction

Example user input:

```
Age: 25
BMI: 23
Sun Exposure: 30 minutes
Skin Exposure: 40%
Fish Intake: 2/week
Physical Activity: 3 hours/week
Indoor Work: 6 hours/day
```

Predicted Vitamin D Level:

```
25.65 ng/ml
```

Vitamin D Status:

```
Insufficient
```

---

## Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- Seaborn

---

## Project Structure

```
vitaminD_prediction/
│
├── VitaminD_Dataset.csv
├── vitD_prediction.ipynb
└── README.md
```

---

## Future Improvements

Possible future enhancements include:

- Adding classification models for Vitamin D deficiency categories
- Integrating real clinical datasets
- Building a web application for user input
- Integrating IoT sensors for real-time sun exposure monitoring

---

## Author

Ayush Kumar
