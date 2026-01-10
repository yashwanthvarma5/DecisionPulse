from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import io
import pandas as pd
import joblib
import shap
import numpy as np
from sklearn.ensemble import IsolationForest

# ----------------------------
# App
# ----------------------------
app = FastAPI(
    title="DecisionPulse API",
    description="Churn Prediction, Explainability & Decision Engine",
    version="1.0.0"
)

# ----------------------------
# CORS (Frontend ↔ Backend)
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Load artifacts
# ----------------------------
FEATURES_PATH = "data/processed/user_features.csv"
MODEL_PATH = "models/gb_model.pkl"
ANOMALY_MODEL_PATH = "models/anomaly_model.pkl"

features = pd.read_csv(FEATURES_PATH)

model = joblib.load(MODEL_PATH)
anomaly_model = joblib.load(ANOMALY_MODEL_PATH)

X = features.drop(columns=["user_id"])
user_ids = features["user_id"]

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)
if isinstance(shap_values, list):
    shap_values = shap_values[1]

# ----------------------------
# Helpers
# ----------------------------
def get_user_index(user_id: int):
    matches = user_ids[user_ids == user_id]
    if matches.empty:
        raise HTTPException(status_code=404, detail="User not found")
    return matches.index[0]


def recommend_action(churn_prob, row, shap_row):
    top_driver = shap_row.abs().idxmax()

    if churn_prob >= 0.8 and row["days_since_last_active"] >= 10:
        return {
            "risk_level": "CRITICAL",
            "action": "Send re-engagement email + push notification",
            "primary_reason": top_driver
        }
    elif churn_prob >= 0.6 and row["session_trend_ratio"] < 0.7:
        return {
            "risk_level": "AT_RISK",
            "action": "Show feature discovery nudge",
            "primary_reason": top_driver
        }
    else:
        return {
            "risk_level": "HEALTHY",
            "action": "No action required",
            "primary_reason": top_driver
        }


def validate_uploaded_data(df: pd.DataFrame, feature_cols: list):
    for col in feature_cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise HTTPException(
                status_code=400,
                detail=f"Column '{col}' must be numeric"
            )

    if df[feature_cols].isnull().any().any():
        raise HTTPException(
            status_code=400,
            detail="Uploaded data contains NaN values"
        )

    if not np.isfinite(df[feature_cols].values).all():
        raise HTTPException(
            status_code=400,
            detail="Uploaded data contains infinite values"
        )

    if (df["days_since_last_active"] < 0).any():
        raise HTTPException(
            status_code=400,
            detail="days_since_last_active cannot be negative"
        )

    if (df["sessions_per_day"] < 0).any():
        raise HTTPException(
            status_code=400,
            detail="sessions_per_day cannot be negative"
        )

    if ((df["active_days_ratio"] < 0) | (df["active_days_ratio"] > 1)).any():
        raise HTTPException(
            status_code=400,
            detail="active_days_ratio must be between 0 and 1"
        )

# ----------------------------
# Routes
# ----------------------------
@app.get("/health")
def health():
    return {"meta": {}, "data": {"status": "ok"}}


@app.get("/predict/{user_id}")
def predict(user_id: int):
    idx = get_user_index(user_id)
    prob = float(model.predict_proba(X.iloc[[idx]])[:, 1][0])
    return {
        "meta": {},
        "data": {
            "user_id": user_id,
            "churn_probability": prob
        }
    }


@app.get("/decision/{user_id}")
def decision(user_id: int):
    idx = get_user_index(user_id)
    prob = float(model.predict_proba(X.iloc[[idx]])[:, 1][0])
    shap_row = pd.Series(shap_values[idx], index=X.columns)
    decision = recommend_action(prob, X.iloc[idx], shap_row)

    return {
        "meta": {},
        "data": {
            "user_id": user_id,
            "churn_probability": prob,
            **decision
        }
    }

# ----------------------------
# Summary Endpoints
# ----------------------------
@app.get("/summary/overview")
def summary_overview():
    probs = model.predict_proba(X)[:, 1]
    return {
        "meta": {},
        "data": {
            "total_users": len(X),
            "avg_churn_probability": float(np.mean(probs)),
            "high_risk_users": int((probs >= 0.8).sum())
        }
    }


@app.get("/summary/risk-distribution")
def risk_distribution():
    probs = model.predict_proba(X)[:, 1]
    return {
        "meta": {},
        "data": {
            "healthy": int((probs < 0.6).sum()),
            "at_risk": int(((probs >= 0.6) & (probs < 0.8)).sum()),
            "critical": int((probs >= 0.8).sum())
        }
    }


@app.get("/summary/anomalies")
def anomaly_summary():
    anomaly_labels = anomaly_model.predict(X)
    return {
        "meta": {},
        "data": {
            "total_anomalies": int((anomaly_labels == -1).sum())
        }
    }

# ----------------------------
# Upload Endpoint
# ----------------------------
@app.post("/upload-data")
def upload_and_analyze(file: UploadFile = File(...)):
    contents = file.file.read()
    df = pd.read_csv(io.BytesIO(contents))

    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded CSV is empty")

    required_cols = set(X.columns.tolist() + ["user_id"])
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise HTTPException(
            status_code=400,
            detail=f"Missing columns: {list(missing)}"
        )

    validate_uploaded_data(df, X.columns.tolist())

    user_ids_upload = df["user_id"]
    X_upload = df[X.columns]

    churn_probs = model.predict_proba(X_upload)[:, 1]

    shap_vals = explainer.shap_values(X_upload)
    if isinstance(shap_vals, list):
        shap_vals = shap_vals[1]

    anomaly_scores = anomaly_model.decision_function(X_upload)
    anomaly_labels = anomaly_model.predict(X_upload)

    results = []
    for i in range(len(df)):
        shap_row = pd.Series(shap_vals[i], index=X.columns)
        decision = recommend_action(
            churn_probs[i],
            X_upload.iloc[i],
            shap_row
        )

        results.append({
            "user_id": int(user_ids_upload.iloc[i]),
            "churn_probability": float(churn_probs[i]),
            "risk_level": decision["risk_level"],
            "recommended_action": decision["action"],
            "primary_reason": decision["primary_reason"],
            "is_anomaly": bool(anomaly_labels[i] == -1),
            "anomaly_score": float(anomaly_scores[i])
        })

    return {
        "meta": {"rows_processed": len(results)},
        "data": results
    }
