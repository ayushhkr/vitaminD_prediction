# Vitamin D Prediction Notebook

## Overview

This project builds and compares machine learning pipelines to estimate Vitamin D levels from non-invasive features and then infer deficiency risk.

The notebook now includes two data tracks:

- A custom Vitamin D dataset (`VitaminD_Dataset.csv`) with lifestyle and body-composition signals.
- A public NHANES (2017-2018) pipeline that predicts serum Vitamin D from demographic, BMI, activity, diet, supplement, seasonality, sun-exposure, and smoking-related features.

The goal is to support screening-style prediction, not replace lab diagnosis.

## What's Updated

The latest notebook version adds the following major updates:

1. Stronger preprocessing and schema robustness

- Handles multiple dataset variants (`VitaminD_Level_ng_ml` or `Risk_Score`).
- Avoids leakage columns (for example `Deficiency_Status`).
- Uses one-hot encoding for feature safety across categorical inputs.
- Applies numeric coercion and fallback target encoding when required.

2. Expanded model suite on the custom dataset

- Linear Regression
- Random Forest Regressor
- Gradient Boosting Regressor
- XGBoost Regressor

3. Clinical prediction outputs

- Predicts continuous Vitamin D level.
- Converts to a binary deficiency decision using clinical threshold logic.

4. Full NHANES regression pipeline

- Pulls multiple NHANES modules directly.
- Cleans non-response codes and implausible physiological values.
- Applies IQR clipping and median imputation.
- Trains/evaluates the same model family for fair comparison.

5. Regression vs classification benchmark

- Compares `Regression -> Threshold` against direct binary classification.
- Reports clinical metrics: Accuracy, F1, ROC-AUC, Sensitivity, Specificity.

6. Improved NHANES performance section

- Additional feature engineering: season, dietary vitamin D, supplement vitamin D, sun exposure, smoking status.
- Polynomial/interactions for non-linear effects.
- Hyperparameter tuning with randomized search for Random Forest and XGBoost.
- Stacking ensemble (RF + XGB + GBR with Ridge meta-model).
- 5-fold CV reporting and top-feature importance visualization.

## Data

### Custom dataset

- File: `VitaminD_Dataset.csv`
- Typical signals: age, gender, BMI, body fat, sun exposure, skin exposure, fish/dairy intake, alcohol, physical activity, indoor work.

### NHANES dataset

- Downloaded in-notebook from official CDC NHANES XPT files.
- Uses merged modules to build a cleaner population-level prediction pipeline.

## Notebook Workflow

1. Import libraries and load custom dataset.
2. EDA and correlation inspection.
3. Preprocess and encode features.
4. Train/test split and baseline model evaluation.
5. Compare model metrics and visualize feature importance.
6. Generate single-person clinical prediction on custom features.
7. Build NHANES pipeline and run same model family.
8. Compare custom vs NHANES outcomes.
9. Compare regression-thresholding vs direct classification.
10. Run improved NHANES pipeline with tuning + stacking + CV.

## Results (Brief)

- On the custom dataset, tree-based models outperform the simple linear baseline in predictive accuracy.
- Feature-importance outputs consistently highlight sunlight and lifestyle-linked variables as major contributors.
- In the NHANES section, the improved pipeline (feature engineering + tuning + stacking) gives stronger and more stable performance than untuned baselines.
- The clinical comparison section shows that both modeling strategies can be used for deficiency screening, with trade-offs between sensitivity and specificity depending on thresholding strategy.
- The notebook ends with sample-person predictions in both `nmol/L` and `ng/mL`, plus a direct deficiency label.

## Metrics Snapshot Template

Use these tables to paste the latest notebook outputs after each run.

### Custom Dataset Regression Metrics

| Model             |  R2 | MAE | RMSE |
| ----------------- | --: | --: | ---: |
| Linear Regression |     |     |      |
| Random Forest     |     |     |      |
| Gradient Boosting |     |     |      |
| XGBoost           |     |     |      |

Best model this run:

### NHANES Baseline Regression Metrics

| Model             |  R2 | MAE | RMSE |
| ----------------- | --: | --: | ---: |
| Linear Regression |     |     |      |
| Random Forest     |     |     |      |
| Gradient Boosting |     |     |      |
| XGBoost           |     |     |      |

Best model this run:

### NHANES Improved Pipeline Metrics

| Model                 |  R2 | MAE | RMSE |
| --------------------- | --: | --: | ---: |
| Linear Regression     |     |     |      |
| Random Forest (tuned) |     |     |      |
| XGBoost (tuned)       |     |     |      |
| Gradient Boosting     |     |     |      |
| Stacking Ensemble     |     |     |      |

Best model this run:

5-fold CV for best model: mean = , std =

### Clinical Binary Task (Regression vs Classification)

| Dataset | Approach                | Accuracy |  F1 | ROC-AUC | Sensitivity | Specificity |
| ------- | ----------------------- | -------: | --: | ------: | ----------: | ----------: |
| Custom  | Regression -> Threshold |          |     |         |             |             |
| Custom  | Direct Classification   |          |     |         |             |             |
| NHANES  | Regression -> Threshold |          |     |         |             |             |
| NHANES  | Direct Classification   |          |     |         |             |             |

## Tech Stack

- Python
- pandas, numpy
- scikit-learn
- xgboost
- matplotlib, seaborn

## Repository Structure

```text
vit D/
|- README.md
|- VitaminD_Dataset.csv
`- vitD prediction.ipynb
```

## How To Run

1. Open `vitD prediction.ipynb` in VS Code/Jupyter.
2. Install required packages in your active environment:

```bash
pip install pandas numpy scikit-learn matplotlib seaborn xgboost
```

3. Run cells top-to-bottom.
4. For NHANES sections, keep internet enabled because data is downloaded from CDC endpoints.

## Notes

- This is a research/education pipeline for screening insight.
- Clinical diagnosis must rely on professional medical assessment and validated lab testing.

## Author

Ayush Kumar
