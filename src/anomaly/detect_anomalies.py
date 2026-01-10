import pandas as pd
import numpy as np
import joblib
import os

from sklearn.ensemble import IsolationForest

# ----------------------------
# Paths
# ----------------------------
FEATURES_PATH = "data/processed/user_features.csv"
MODEL_PATH = "models/anomaly_model.pkl"

os.makedirs("models", exist_ok=True)
os.makedirs("reports/anomaly", exist_ok=True)

# ----------------------------
# Load data
# ----------------------------
features = pd.read_csv(FEATURES_PATH)
user_ids = features["user_id"]
X = features.drop(columns=["user_id"])

# ----------------------------
# Train Isolation Forest
# ----------------------------
anomaly_model = IsolationForest(
    n_estimators=200,
    contamination=0.05,  # assume 5% abnormal users
    random_state=42
)

anomaly_model.fit(X)

# ----------------------------
# Predict anomalies
# ----------------------------
anomaly_scores = anomaly_model.decision_function(X)
anomaly_labels = anomaly_model.predict(X)  # -1 = anomaly, 1 = normal

results = pd.DataFrame({
    "user_id": user_ids,
    "anomaly_score": anomaly_scores,
    "is_anomaly": anomaly_labels == -1
})

# ----------------------------
# Save outputs
# ----------------------------
joblib.dump(anomaly_model, MODEL_PATH)
results.to_csv("reports/anomaly/user_anomalies.csv", index=False)

print("✅ Anomaly detection complete")
print(results["is_anomaly"].value_counts())
