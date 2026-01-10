import pandas as pd
import shap
import joblib
import os

# ----------------------------
# Paths
# ----------------------------
FEATURES_PATH = "data/processed/user_features.csv"
LABELS_PATH = "data/processed/churn_labels.csv"
MODEL_PATH = "models/gb_model.pkl"
SCALER_PATH = "models/scaler.pkl"

# ----------------------------
# Load data
# ----------------------------
X = pd.read_csv(FEATURES_PATH)
y = pd.read_csv(LABELS_PATH)

data = X.merge(y, on="user_id")

user_ids = data["user_id"]
X_model = data.drop(columns=["user_id", "churned"])

# ----------------------------
# Load model
# ----------------------------
model = joblib.load(MODEL_PATH)

# ----------------------------
# SHAP Explainer
# ----------------------------
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_model)

# ----------------------------
# Global importance
# ----------------------------
importance = pd.DataFrame({
    "feature": X_model.columns,
    "mean_abs_shap": abs(shap_values).mean(axis=0)
}).sort_values(by="mean_abs_shap", ascending=False)

os.makedirs("reports", exist_ok=True)
importance.to_csv("reports/global_feature_importance.csv", index=False)

print("✅ Global feature importance saved")

# ----------------------------
# Per-user explanation function
# ----------------------------
def explain_user(user_id, top_n=5):
    idx = user_ids[user_ids == user_id].index[0]

    user_shap = pd.Series(
        shap_values[idx],
        index=X_model.columns
    ).sort_values(key=abs, ascending=False)

    explanation = user_shap.head(top_n)

    return explanation


# ----------------------------
# Example explanation
# ----------------------------
example_user = user_ids.sample(1).values[0]
print(f"\n🔍 Explanation for user {example_user}:")
print(explain_user(example_user))
