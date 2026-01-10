import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    confusion_matrix
)

from sklearn.ensemble import GradientBoostingClassifier
import joblib
import os

# ----------------------------
# Paths
# ----------------------------
FEATURES_PATH = "data/processed/user_features.csv"
LABELS_PATH = "data/processed/churn_labels.csv"
MODEL_DIR = "models"

os.makedirs(MODEL_DIR, exist_ok=True)

# ----------------------------
# Load data
# ----------------------------
X = pd.read_csv(FEATURES_PATH)
y = pd.read_csv(LABELS_PATH)

data = X.merge(y, on="user_id")

X = data.drop(columns=["user_id", "churned"])
y = data["churned"]

# ----------------------------
# Train / test split
# ----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

# ----------------------------
# Scaling (for logistic)
# ----------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ----------------------------
# 1️⃣ Logistic Regression (baseline)
# ----------------------------
log_model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced"
)

log_model.fit(X_train_scaled, y_train)

log_preds = log_model.predict(X_test_scaled)
log_probs = log_model.predict_proba(X_test_scaled)[:, 1]

print("\n--- Logistic Regression ---")
print(confusion_matrix(y_test, log_preds))
print(classification_report(y_test, log_preds))
print("ROC-AUC:", roc_auc_score(y_test, log_probs))

# ----------------------------
# 2️⃣ Gradient Boosting (production-grade)
# ----------------------------
gb_model = GradientBoostingClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=3,
    random_state=42
)

gb_model.fit(X_train, y_train)

gb_preds = gb_model.predict(X_test)
gb_probs = gb_model.predict_proba(X_test)[:, 1]

print("\n--- Gradient Boosting ---")
print(confusion_matrix(y_test, gb_preds))
print(classification_report(y_test, gb_preds))
print("ROC-AUC:", roc_auc_score(y_test, gb_probs))

# ----------------------------
# Save models
# ----------------------------
joblib.dump(log_model, f"{MODEL_DIR}/logistic_model.pkl")
joblib.dump(gb_model, f"{MODEL_DIR}/gb_model.pkl")
joblib.dump(scaler, f"{MODEL_DIR}/scaler.pkl")

print("\n✅ Models trained and saved")
