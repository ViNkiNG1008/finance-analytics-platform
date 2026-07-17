"""
Phase 6: rule-based textual insights (no ML) — compares recent months,
flags categories with rising spend, and flags over-budget categories.
"""
from datetime import date
from typing import List

from sqlalchemy.engine import Engine

from src.db.queries import get_monthly_trend, get_category_breakdown, get_budget_vs_actual


def generate_insights(engine: Engine, user_id: int) -> List[str]:
    """Return a list of human-readable insight strings, scoped to one user."""
    insights: List[str] = []

    trend_df = get_monthly_trend(engine, user_id, months=12).sort_values("month")

    # 1. Month-over-month expense change
    if len(trend_df) >= 2:
        last = trend_df.iloc[-1]
        prev = trend_df.iloc[-2]
        if prev["expense"] > 0:
            pct_change = (last["expense"] - prev["expense"]) / prev["expense"] * 100
            direction = "up" if pct_change > 0 else "down"
            insights.append(
                f"Expenses are {direction} {abs(pct_change):.0f}% vs last month "
                f"(₹{last['expense']:,.0f} vs ₹{prev['expense']:,.0f})."
            )

    # 2. Savings rate trend
    if len(trend_df) >= 2:
        last = trend_df.iloc[-1]
        prev = trend_df.iloc[-2]
        last_sr = ((last["income"] - last["expense"]) / last["income"] * 100) if last["income"] > 0 else None
        prev_sr = ((prev["income"] - prev["expense"]) / prev["income"] * 100) if prev["income"] > 0 else None
        if last_sr is not None and prev_sr is not None:
            delta = last_sr - prev_sr
            if abs(delta) >= 1:
                direction = "improved" if delta > 0 else "dropped"
                insights.append(
                    f"Savings rate {direction} by {abs(delta):.1f} percentage points "
                    f"({prev_sr:.1f}% → {last_sr:.1f}%)."
                )

    # 3. Biggest expense category
    cat_df = get_category_breakdown(engine, user_id)
    if not cat_df.empty:
        top = cat_df.iloc[0]
        total = cat_df["total"].sum()
        share = (top["total"] / total * 100) if total > 0 else 0
        insights.append(
            f"'{top['category_name']}' is your biggest expense category, "
            f"making up {share:.0f}% of total spend."
        )

    # 4. Over-budget categories this month
    today = date.today()
    bva_df = get_budget_vs_actual(engine, user_id, year=today.year, month=today.month)
    if not bva_df.empty:
        over = bva_df[(bva_df["monthly_limit"] > 0) & (bva_df["actual_spent"] > bva_df["monthly_limit"])]
        for _, row in over.iterrows():
            over_amount = row["actual_spent"] - row["monthly_limit"]
            insights.append(
                f"You're ₹{over_amount:,.0f} over budget on '{row['category_name']}' this month."
            )

    if not insights:
        insights.append("Not enough transaction history yet to generate insights — upload more statements.")

    return insights