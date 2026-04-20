# Vitamin D Prediction

This repository is organized into two clear versions of the same project:

- a simple notebook version for college submission
- an advanced version for personal project work

## Project Structure

```text
vitaminD_prediction/
|- data/
|  `- VitaminD_Dataset.csv
|- notebooks/
|  |- vitaminD_college.ipynb
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

## Versions

### `notebooks/vitaminD_college.ipynb`

This is the simple version for college submission.

It includes:

- custom dataset only
- basic preprocessing
- train/test split
- simple regression models
- evaluation with R2, MAE, and RMSE
- feature importance plot
- one sample prediction

It intentionally removes:

- NHANES analysis
- complex pipelines
- cross-validation
- hyperparameter tuning
- advanced feature engineering

### `notebooks/vitaminD_advanced.ipynb`

This is the full personal-project notebook.

It includes:

- custom dataset work
- NHANES experiments
- focused feature engineering
- multiple models including XGBoost
- tuning and comparison work
- advanced analysis and visualizations

## Data

The custom dataset is stored in:

- `data/VitaminD_Dataset.csv`

Main target column:

- `VitaminD_Level_ng_ml`

Main input features include:

- age
- gender
- weight
- height
- BMI
- body fat
- sun exposure
- skin exposure
- fish and dairy intake
- alcohol intake
- physical activity
- indoor work hours

## Advanced Code

Reusable code lives in `src/`:

- `preprocessing.py`
  - dataset loading
  - schema validation
  - preprocessing pipeline
- `train.py`
  - model training
  - cross-validation
  - artifact saving
- `evaluate.py`
  - metric review
  - sample prediction from the saved model

## Artifacts

Generated outputs are stored in:

- `artifacts/models/`
- `artifacts/metrics/`
- `artifacts/plots/`

Current saved outputs may include:

- trained model file
- regression metrics
- prediction outputs
- run summary

## Installation

Create or activate your environment, then run:

```bash
pip install -r requirements.txt
```

## Run The Advanced Code

Train the advanced version:

```bash
python src/train.py
```

Review saved metrics:

```bash
python src/evaluate.py --mode metrics
```

Run one sample prediction:

```bash
python src/evaluate.py --mode predict
```

## Notes

- The college notebook is meant to stay simple and easy to explain.
- The advanced notebook and `src/` code are for stronger project presentation and experimentation.
- This is a machine learning screening project, not a clinical diagnostic tool.
