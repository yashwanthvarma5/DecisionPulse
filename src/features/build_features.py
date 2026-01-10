import pandas as pd
import numpy as np
from scipy.stats import entropy

# ----------------------------
# Load data
# ----------------------------
def load_events(path="data/raw/events.csv"):
    df = pd.read_csv(path, parse_dates=["event_time"])
    return df


# ----------------------------
# Core Feature Builder
# ----------------------------
def build_user_features(events: pd.DataFrame):
    events["date"] = events["event_time"].dt.date

    # Filter only meaningful activity
    activity = events[events["event_type"].isin(["login", "feature_use"])]

    # ----------------------------
    # Session-level features
    # ----------------------------
    sessions = activity.groupby(["user_id", "date"]).agg(
        daily_sessions=("event_type", "count"),
        avg_session_duration=("session_duration", "mean")
    ).reset_index()

    # ----------------------------
    # User aggregates
    # ----------------------------
    user_agg = sessions.groupby("user_id").agg(
        total_sessions=("daily_sessions", "sum"),
        avg_session_duration=("avg_session_duration", "mean"),
        active_days=("date", "nunique"),
        daily_activity_std=("daily_sessions", "std")
    ).reset_index()

    observation_days = sessions["date"].nunique()
    user_agg["sessions_per_day"] = user_agg["total_sessions"] / observation_days
    user_agg["active_days_ratio"] = user_agg["active_days"] / observation_days

    # ----------------------------
    # Recency
    # ----------------------------
    last_active = sessions.groupby("user_id")["date"].max().reset_index()
    max_date = sessions["date"].max()

    last_active["days_since_last_active"] = (
        pd.to_datetime(max_date) - pd.to_datetime(last_active["date"])
    ).dt.days

    user_agg = user_agg.merge(
        last_active[["user_id", "days_since_last_active"]],
        on="user_id",
        how="left"
    )

    # ----------------------------
    # Trend features (last 7d vs prev 7d)
    # ----------------------------
    sessions["date"] = pd.to_datetime(sessions["date"])
    cutoff = sessions["date"].max() - pd.Timedelta(days=7)

    last_7d = sessions[sessions["date"] >= cutoff]
    prev_7d = sessions[sessions["date"] < cutoff]

    last_7d_agg = last_7d.groupby("user_id")["daily_sessions"].sum().rename("sessions_last_7d")
    prev_7d_agg = prev_7d.groupby("user_id")["daily_sessions"].sum().rename("sessions_prev_7d")

    trends = pd.concat([last_7d_agg, prev_7d_agg], axis=1).fillna(0)
    trends["session_trend_ratio"] = (
        trends["sessions_last_7d"] / (trends["sessions_prev_7d"] + 1)
    )

    user_agg = user_agg.merge(trends, on="user_id", how="left")

    # ----------------------------
    # Feature diversity & entropy
    # ----------------------------
    feature_usage = activity.dropna(subset=["feature_name"])

    feature_counts = (
        feature_usage
        .groupby(["user_id", "feature_name"])
        .size()
        .reset_index(name="count")
    )

    feature_entropy = (
        feature_counts
        .groupby("user_id")
        .apply(lambda x: entropy(x["count"]))
        .rename("feature_entropy")
        .reset_index()
    )

    unique_features = (
        feature_counts
        .groupby("user_id")["feature_name"]
        .nunique()
        .rename("unique_features_used")
        .reset_index()
    )

    user_agg = (
        user_agg
        .merge(feature_entropy, on="user_id", how="left")
        .merge(unique_features, on="user_id", how="left")
    )

    # ----------------------------
    # Cleanup
    # ----------------------------
    user_agg.fillna(0, inplace=True)

    return user_agg


# ----------------------------
# Run pipeline
# ----------------------------
if __name__ == "__main__":
    events = load_events()
    features = build_user_features(events)

    features.to_csv("data/processed/user_features.csv", index=False)
    print("✅ Feature engineering complete")
    print(features.head())
