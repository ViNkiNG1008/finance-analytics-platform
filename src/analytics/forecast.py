"""
Phase 6: forecast next month's total expense using a simple linear
regression over historical monthly expense totals.

Intentionally simple (resume-portfolio scope, not a production
forecasting system) — a linear trend fit on however many months of
history exist, extrapolated one month forward.
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sqlalchemy.engine import Engine

from src.db.queries import get_monthly_trend


def forecast_next_month_expense(engine: Engine, user_id: int, months_history: int = 12) -> dict:
    """
    Fit a linear trend on the last `months_history` months of expense
    totals (for one user) and predict the next month's expense.

    Returns a dict with history (DataFrame), forecast_month (Timestamp),
    forecast_expense (float), and trend_confidence ("low"/"medium"/"high").
    All values are None if there isn't enough history to fit a trend.
    """
    trend_df = get_monthly_trend(engine, user_id, months=months_history)

    if trend_df.empty or len(trend_df) < 2:
        return {
            "history": trend_df,
            "forecast_month": None,
            "forecast_expense": None,
            "trend_confidence": None,
        }

    trend_df = trend_df.sort_values("month").reset_index(drop=True)
    X = np.arange(len(trend_df)).reshape(-1, 1)
    y = trend_df["expense"].values

    model = LinearRegression()
    model.fit(X, y)

    next_x = np.array([[len(trend_df)]])
    forecast_value = max(float(model.predict(next_x)[0]), 0.0)  # expenses can't be negative

    last_month = pd.Timestamp(trend_df["month"].iloc[-1])
    forecast_month = (last_month + pd.DateOffset(months=1)).replace(day=1)

    if len(trend_df) >= 6:
        confidence = "high"
    elif len(trend_df) >= 3:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "history": trend_df,
        "forecast_month": forecast_month,
        "forecast_expense": forecast_value,
        "trend_confidence": confidence,
    }