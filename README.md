# Vitamin D Prediction

## Live Deployment

Render app link:

- [https://vitamind-predictor-advanced.onrender.com](https://vitamind-predictor-advanced.onrender.com)

Note:

- The free Render instance may take a short time to wake up on first request.

This repository contains a machine learning project for predicting Vitamin D level from non-invasive features. It is organized into two parallel versions:

- a simpler notebook version for college submission
- a more detailed version for personal project and experimentation

The project uses:

- a custom Vitamin D dataset stored locally
- a public NHANES dataset section inside the notebooks to show real-world health data usage

## Project Goal

The aim is to estimate Vitamin D level and identify likely deficiency risk using lifestyle, body-composition, and demographic features.

This is a screening-oriented machine learning project for learning and analysis. It is not a clinical diagnostic tool.

## Repository Structure

```text
vitaminD_prediction/
|- data/
|  `- VitaminD_Dataset.csv
|- notebooks/
|  |- vitaminD_simple.ipynb
|  `- vitaminD_advanced.ipynb
|- src/
|  |- preprocessing.py
|  |- train.py
|  `- evaluate.py
|- artifacts/
|  |- models/
|  |- metrics/
|  `- plots/
|- requirements.txt
|- README.md
`- .gitignore
```

## Dataset

### Custom Dataset

Main target:

- `VitaminD_Level_ng_ml`
  Typical input features:

- `Age`
- `Gender`
- `Weight_kg`
- `Height_cm`
- `BMI`
- `BodyFat_percent`
- `Sun_Exposure_min`
- `Skin_Exposure_percent`
- `Alcohol_units_week`
- `Fish_intake_week`
- `Dairy_intake_week`
- `Physical_activity_hours_week`
- `Indoor_work_hours_day`

Optional columns such as `Skin_tone`, `Sunscreen_Use`, `VitaminD_Category`, `Deficiency_Status`, and `Risk_Score` are removed when needed to avoid leakage or unnecessary complexity.

### NHANES Dataset

The notebooks also use NHANES 2017-2018 public health data loaded directly from CDC files. This helps make the project look more realistic by showing how the same prediction idea can be tested on real-world population data.

The simpler NHANES workflow uses only a small set of understandable features such as:

- age
- sex
- race/ethnicity
- BMI
- season
- one physical activity feature

## Notebook Versions

### `notebooks/vitaminD_simple.ipynb`

This is the simpler version for college submission.

It keeps the original custom-dataset pipeline and visual flow, and now also includes a simple NHANES section at the end.

Included in this notebook:

- custom dataset loading and preprocessing
- train/test split
- four regression models
  - Linear Regression
  - Random Forest
  - XGBoost
  - Gradient Boosting
- evaluation with R2, MAE, RMSE
- correlation heatmap
- model comparison plot
- feature importance plot
- actual vs predicted plot
- one custom dataset sample prediction
- one NHANES sample prediction

This notebook is meant to stay easier to explain during submission, presentation, or viva.

### `notebooks/vitaminD_advanced.ipynb`

This is the personal-project version.

It contains the broader project work, including:

- custom dataset experiments
- NHANES modeling
- focused NHANES feature selection
- additional comparisons
- advanced experimentation beyond the college version

Use this notebook when you want the full project story instead of the simpler submission version.

## Advanced Python Code

Reusable code for the advanced version is stored in `src/`.

### `src/preprocessing.py`

Handles:

- dataset loading
- required-column validation
- feature/target preparation
- preprocessing pipeline creation

### `src/train.py`

Handles:

- model training
- model comparison
- cross-validation for the advanced script workflow
- binary deficiency evaluation
- saving model and metrics into `artifacts/`

### `src/evaluate.py`

Handles:

- printing saved metrics
- loading the saved best model
- running one sample prediction

## Models Used

Across the project, the main models used are:

- Linear Regression
- Random Forest Regressor
- Gradient Boosting Regressor
- XGBoost Regressor

For classification-style deficiency screening in the advanced script workflow:

- Random Forest Classifier

## Evaluation Metrics

The project mainly reports:

- R2 Score
- MAE
- RMSE

For the advanced classification-style screening workflow, it also reports:

- Accuracy
- F1 Score
- ROC-AUC
- Sensitivity
- Specificity

## Saved Artifacts

Generated outputs are stored in:

- `artifacts/models/`
- `artifacts/metrics/`
- `artifacts/plots/`

Current saved files may include:

- `artifacts/models/best_model.joblib`
- `artifacts/metrics/regression_metrics.csv`
- `artifacts/metrics/test_predictions.csv`
- `artifacts/metrics/run_summary.json`

## Installation

Create or activate a Python environment, then install dependencies:

```bash
pip install -r requirements.txt
```

## How To Run

### Open the notebooks

Run either notebook in Jupyter or VS Code:

- `notebooks/vitaminD_simple.ipynb`
- `notebooks/vitaminD_advanced.ipynb`

Note:

- the custom dataset is read from `../data/VitaminD_Dataset.csv`
- the NHANES sections require internet access because the data is fetched from CDC endpoints

### Run the advanced script version

Train the advanced script workflow:

```bash
python src/train.py
```

View saved metrics:

```bash
python src/evaluate.py --mode metrics
```

Run one saved-model sample prediction:

```bash
python src/evaluate.py --mode predict
```

## Current Project Story

The project is designed so you can present it in two ways:

- `college notebook`: clean, understandable, visually complete, and easier to defend
- `advanced notebook + src/ scripts`: stronger personal-project version with more technical depth

This makes the repository useful both for academic submission and for showcasing a more serious machine learning project.

## Limitations

- Vitamin D prediction from non-invasive features is inherently noisy
- NHANES performance is modest because serum Vitamin D depends on many factors not fully captured here
- results should be treated as educational and screening-oriented, not medically definitive

## Author

Ayush kumar
