import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

# ----------------------------
# Configuration
# ----------------------------
NUM_USERS = 5000
DAYS_OBSERVED = 30
CHURN_INACTIVITY_DAYS = 14
SEED = 42

np.random.seed(SEED)
random.seed(SEED)

FEATURES = [
    "dashboard",
    "search",
    "analytics",
    "notifications",
    "profile",
    "settings"
]

DEVICES = ["android", "ios", "web"]

EVENT_TYPES = ["login", "feature_use", "logout"]


# ----------------------------
# Helper functions
# ----------------------------
def generate_user_profile():
    """Simulate different user engagement personalities"""
    return {
        "base_activity": np.random.choice([0.3, 0.6, 0.9], p=[0.3, 0.5, 0.2]),
        "decay_rate": np.random.uniform(0.0, 0.05),
        "preferred_device": random.choice(DEVICES)
    }


def simulate_day_activity(base_prob, decay, day):
    """Activity probability decays over time"""
    return max(0, base_prob - decay * day)


# ----------------------------
# Main Generator
# ----------------------------
def generate_events():
    start_date = datetime.now() - timedelta(days=DAYS_OBSERVED + CHURN_INACTIVITY_DAYS)
    all_events = []

    churn_labels = {}

    for user_id in range(1, NUM_USERS + 1):
        profile = generate_user_profile()
        inactive_streak = 0
        churned = False

        for day in range(DAYS_OBSERVED + CHURN_INACTIVITY_DAYS):
            current_date = start_date + timedelta(days=day)
            activity_prob = simulate_day_activity(
                profile["base_activity"], profile["decay_rate"], day
            )

            active_today = np.random.rand() < activity_prob

            if not active_today:
                inactive_streak += 1
            else:
                inactive_streak = 0

            if inactive_streak >= CHURN_INACTIVITY_DAYS:
                churned = True

            if active_today:
                session_duration = np.random.gamma(shape=2, scale=10)

                # Login
                all_events.append({
                    "user_id": user_id,
                    "event_time": current_date + timedelta(minutes=random.randint(0, 60)),
                    "event_type": "login",
                    "session_duration": session_duration,
                    "feature_name": None,
                    "device_type": profile["preferred_device"]
                })

                # Feature usage
                for _ in range(np.random.randint(1, 4)):
                    all_events.append({
                        "user_id": user_id,
                        "event_time": current_date + timedelta(minutes=random.randint(5, 120)),
                        "event_type": "feature_use",
                        "session_duration": session_duration,
                        "feature_name": random.choice(FEATURES),
                        "device_type": profile["preferred_device"]
                    })

                # Logout
                all_events.append({
                    "user_id": user_id,
                    "event_time": current_date + timedelta(minutes=random.randint(120, 180)),
                    "event_type": "logout",
                    "session_duration": session_duration,
                    "feature_name": None,
                    "device_type": profile["preferred_device"]
                })

        churn_labels[user_id] = int(churned)

    events_df = pd.DataFrame(all_events)
    churn_df = pd.DataFrame.from_dict(
        churn_labels, orient="index", columns=["churned"]
    ).reset_index().rename(columns={"index": "user_id"})

    return events_df, churn_df


# ----------------------------
# Run & Save
# ----------------------------
if __name__ == "__main__":
    events, churn = generate_events()

    events.to_csv("data/raw/events.csv", index=False)
    churn.to_csv("data/processed/churn_labels.csv", index=False)

    print("✅ Event generation complete")
    print(events.head())
    print(churn["churned"].value_counts())
