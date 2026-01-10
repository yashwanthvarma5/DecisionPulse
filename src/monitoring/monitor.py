import pandas as pd
import numpy as np
import joblib
import os

# ----------------------------
# Paths
# ----------------------------
FEATURES_PATH = "data/processed/user_features.csv"
MODEL_PATH = "models/gb_model.pkl"
BASELINE_PATH = "reports/monitoring/baseline_stats.csv"

os.makedirs("reports/monitoring", exist_ok=True)

# ----------------------------
# Load artifacts
# ----------------------------
features = pd.read_csv(FEATURES_PATH)
model = joblib.load(MODEL_PATH)

X = features.drop(columns=["user_id"])

# ----------------------------
# Prediction confidence monitoring
# ----------------------------
probs = model.predict_proba(X)[:, 1]

confidence_report = {
    "mean_probability": float(np.mean(probs)),
    "std_probability": float(np.std(probs)),
    "high_confidence_rate": float(np.mean((probs > 0.9) | (probs < 0.1)))
}

confidence_df = pd.DataFrame([confidence_report])
confidence_df.to_csv("reports/monitoring/prediction_confidence.csv", index=False)

print("✅ Prediction confidence report saved")

# ----------------------------
# Baseline creation (first run only)
# ----------------------------
if not os.path.exists(BASELINE_PATH):
    baseline = X.describe().loc[["mean", "std"]].T
    baseline.to_csv(BASELINE_PATH)
    print("✅ Baseline statistics created")
else:
    baseline = pd.read_csv(BASELINE_PATH, index_col=0)
    print("✅ Baseline statistics loaded")

# ----------------------------
# Drift detection
# ----------------------------
current_stats = X.describe().loc[["mean", "std"]].T

drift = abs(current_stats["mean"] - baseline["mean"]) / (baseline["std"] + 1e-6)
drift_df = drift.reset_index()
drift_df.columns = ["feature", "relative_mean_shift"]

drift_df.to_csv("reports/monitoring/data_drift.csv", index=False)

# ----------------------------
# Alert logic
# ----------------------------
ALERT_THRESHOLD = 2.0  # 2 std deviation shift

alerts = drift_df[drift_df["relative_mean_shift"] > ALERT_THRESHOLD]

if not alerts.empty:
    print("⚠️ DRIFT ALERT:")
    print(alerts)
else:
    print("✅ No significant drift detected")
