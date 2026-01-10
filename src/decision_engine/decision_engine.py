import pandas as pd
import joblib
import shap

# ----------------------------
# Paths
# ----------------------------
FEATURES_PATH = "data/processed/user_features.csv"
MODEL_PATH = "models/gb_model.pkl"

# ----------------------------
# Load artifacts
# ----------------------------
features = pd.read_csv(FEATURES_PATH)
model = joblib.load(MODEL_PATH)

user_ids = features["user_id"]
X = features.drop(columns=["user_id"])

# ----------------------------
# Predict churn probability
# ----------------------------
churn_probs = model.predict_proba(X)[:, 1]
features["churn_probability"] = churn_probs

# ----------------------------
# SHAP for explanation drivers
# ----------------------------
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

# ----------------------------
# Decision Logic
# ----------------------------
def recommend_action(row, shap_row):
    top_driver = shap_row.abs().idxmax()

    if row["churn_probability"] >= 0.8 and row["days_since_last_active"] >= 10:
        return "CRITICAL: Send re-engagement email + push notification", top_driver

    elif row["churn_probability"] >= 0.6 and row["session_trend_ratio"] < 0.7:
        return "AT RISK: Show feature discovery nudge", top_driver

    else:
        return "HEALTHY: No action required", top_driver


# ----------------------------
# Apply decisions
# ----------------------------
decisions = []

for i, row in features.iterrows():
    action, driver = recommend_action(row, pd.Series(shap_values[i], index=X.columns))
    decisions.append({
        "user_id": row["user_id"],
        "churn_probability": row["churn_probability"],
        "risk_level": action.split(":")[0],
        "recommended_action": action,
        "primary_reason": driver
    })

decision_df = pd.DataFrame(decisions)

decision_df.to_csv("reports/user_decisions.csv", index=False)

print("✅ Decision engine executed")
print(decision_df.head())
