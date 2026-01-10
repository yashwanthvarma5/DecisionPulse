# DecisionPulse 🚀

### End-to-End User Behavior & Decision Intelligence System

DecisionPulse is a production-style Machine Learning system that predicts user churn from SaaS application usage data, explains _why_ a user is at risk using model explainability, and recommends concrete retention actions through a decision engine.

Unlike typical ML projects that stop at prediction, DecisionPulse completes the full **decision intelligence loop** — from raw event telemetry to business-ready actions — and exposes everything through a FastAPI service.

## 📌 Problem Statement

In many SaaS and consumer applications, user churn is identified **too late** — often only after users have already disengaged. While machine learning models can predict churn, most systems fail to explain _why_ users are leaving or _what action_ should be taken to prevent it.

As a result, product and growth teams struggle with:

- Black-box churn predictions with no reasoning
- Reactive retention strategies instead of proactive ones
- Lack of actionable insights at the individual user level

## 🎯 Motivation

The goal of DecisionPulse is to move beyond churn prediction and build a **decision intelligence system** that:

- Detects early signs of disengagement
- Explains behavioral drivers behind churn predictions
- Translates model outputs into concrete, human-readable actions

This project is designed to mirror how real-world ML systems are built and used in production SaaS environments.

## 🏗️ System Architecture

DecisionPulse is designed as a modular, production-style ML system. Each component is independently built but seamlessly integrated to form a complete decision pipeline.

### End-to-End Flow

1. **Event Generation**

   - Synthetic SaaS user activity events are generated to simulate real-world application usage.
   - Events include logins, feature usage, session durations, and devices.

2. **Feature Engineering**

   - Raw event logs are transformed into user-level behavioral features.
   - Features capture recency, frequency, engagement decay, usage diversity, and activity trends.

3. **Churn Prediction**

   - A baseline Logistic Regression model is trained for interpretability.
   - A Gradient Boosting model is used for high-performance churn prediction.

4. **Explainability Layer**

   - SHAP (SHapley Additive exPlanations) is used to explain predictions.
   - Provides both global feature importance and per-user explanations.

5. **Decision Engine**

   - Combines churn probability and behavioral drivers.
   - Categorizes users into risk tiers and recommends concrete retention actions.

6. **API Layer**
   - All predictions, explanations, and decisions are exposed via a FastAPI service.
   - Enables real-time consumption by downstream systems or dashboards.

### Architecture Summary

```text
Raw Events
   ↓
Feature Engineering
   ↓
Churn Prediction Model
   ↓
Explainability (SHAP)
   ↓
Decision Engine
   ↓
FastAPI Service
```

## 🛠️ Tech Stack

**Programming Language**

- Python 3.10

**Data & Feature Engineering**

- Pandas
- NumPy
- SciPy

**Machine Learning**

- Scikit-learn
- Gradient Boosting Classifier
- Logistic Regression (baseline)

**Explainability**

- SHAP (SHapley Additive exPlanations)

**Decision Intelligence**

- Rule-based decision engine built on top of ML + SHAP outputs

**API & Serving**

- FastAPI
- Uvicorn

**Model Persistence**

- Joblib

**Development Tools**

- VS Code
- PowerShell

## 📊 Dataset Design & Churn Definition

### Synthetic SaaS Telemetry

Instead of relying on a pre-labeled churn dataset, DecisionPulse uses **synthetic event-level SaaS telemetry** designed to closely mirror real-world application usage.

Each event represents a user interaction such as:

- Login
- Feature usage
- Logout
- Session duration
- Device type

This approach provides full control over user behavior patterns, engagement decay, and inactivity — enabling realistic churn modeling.

### Churn Definition

Churn is defined **behaviorally**, not artificially.

A user is labeled as **churned (1)** if:

- The user has **no login or feature usage events for 14 consecutive days** following the observation window.

Otherwise:

- The user is labeled as **active (0)**.

This definition reflects how real SaaS companies identify disengagement based on inactivity rather than explicit cancellation events.

### Why This Matters

- Prevents label leakage
- Encourages realistic feature engineering
- Aligns model predictions with real product decisions

This design ensures that churn predictions are explainable, defensible, and production-relevant.

## 🤖 Modeling Approach & Results

### Modeling Strategy

DecisionPulse follows a two-stage modeling approach:

1. **Baseline Model**

   - Logistic Regression with class balancing
   - Used to validate feature quality and ensure interpretability

2. **Production Model**
   - Gradient Boosting Classifier
   - Captures non-linear engagement decay and interaction effects
   - Used for final predictions and decision-making

The focus is placed on:

- Recall for churned users (early risk detection)
- ROC-AUC for overall ranking quality
- Reducing false negatives (missed churners)

---

### Model Performance

| Model               | ROC-AUC | Churn Recall |
| ------------------- | ------- | ------------ |
| Logistic Regression | ~0.997  | ~0.97        |
| Gradient Boosting   | ~0.999  | ~0.99        |

These results demonstrate that the engineered behavioral features strongly capture disengagement patterns and generalize well across users.

---

### Key Observations

- Even a linear baseline performs exceptionally well, validating feature relevance.
- Gradient Boosting further improves recall by modeling non-linear trends.
- Performance aligns with the behavioral churn definition, avoiding artificial leakage.

## 🔍 Explainability & Decision Intelligence

### Explainability with SHAP

DecisionPulse integrates **SHAP (SHapley Additive exPlanations)** to make churn predictions transparent and trustworthy.

Two levels of explainability are provided:

- **Global Explainability**

  - Identifies which behavioral features drive churn across the entire user base
  - Helps product teams understand systemic engagement issues

- **Local (Per-User) Explainability**
  - Explains why an individual user is predicted to churn
  - Highlights the most influential behavioral drivers for that user

Example explanation:

> A user is predicted to churn primarily due to prolonged inactivity and a sharp decline in recent session frequency.

---

### Decision Engine

Rather than stopping at explanations, DecisionPulse includes a **decision engine** that converts predictions into actions.

The decision engine:

- Combines churn probability with behavioral drivers
- Categorizes users into risk tiers (Critical, At Risk, Healthy)
- Recommends concrete, human-readable retention actions

#### Example Decision Rules

- **Critical**

  - High churn probability and long inactivity
  - Action: Re-engagement email + push notification

- **At Risk**

  - Moderate churn probability and declining engagement
  - Action: Feature discovery or in-app nudge

- **Healthy**
  - Low churn probability
  - Action: No intervention required

This closes the gap between machine learning output and real business decisions.

## 🌐 API Endpoints & Usage

DecisionPulse exposes all functionality through a **FastAPI** service, enabling real-time access to predictions, explanations, and decisions.

### Available Endpoints

| Endpoint              | Description                                     |
| --------------------- | ----------------------------------------------- |
| `/health`             | Health check for the service                    |
| `/predict/{user_id}`  | Returns churn probability for a user            |
| `/explain/{user_id}`  | Returns top behavioral drivers using SHAP       |
| `/decision/{user_id}` | Returns churn risk level and recommended action |
| `/users/critical`     | Lists highest-risk users                        |

---

### Example API Response

**GET `/decision/688`**

```json
{
  "user_id": 688,
  "churn_probability": 0.91,
  "risk_level": "CRITICAL",
  "action": "Send re-engagement email + push notification",
  "primary_reason": "days_since_last_active"
}
```
