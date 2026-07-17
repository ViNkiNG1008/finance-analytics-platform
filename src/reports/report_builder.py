"""
Aggregates existing query outputs into a single report data structure
for a given date range. Reused by CSV, PDF, and Excel exporters.
"""
from dataclasses import dataclass, field
from datetime import date
from typing import List, Dict, Any
import pandas as pd

from src.db.queries import (
    get_summary_metrics,
    get_category_breakdown,
    get_top_merchants,
    get_budget_vs_actual,
    get_transactions_for_recurring_check,
)
from src.analytics.recurring import detect_recurring


@dataclass
class ReportData:
    start_date: date
    end_date: date
    summary: Dict[str, Any] = field(default_factory=dict)
    category_breakdown: pd.DataFrame = None
    top_merchants: pd.DataFrame = None
    budget_vs_actual: pd.DataFrame = None
    budget_month: date = None  # first day of the month the budget table covers
    recurring_payments: List[Any] = field(default_factory=list)


def build_report(engine, user_id: int, start_date: date, end_date: date) -> ReportData:
    """
    Pulls all report sections for the given date range and user using the
    existing query functions.

    Note: get_budget_vs_actual is inherently a single-month query (budgets
    are set per calendar month), so it does not take a date range. We use
    the month containing `end_date` — i.e. the most recent month in the
    selected range — and expose that as `budget_month` so exporters can
    label the section clearly (e.g. "Budget vs Actual — June 2026").
    """
    summary = get_summary_metrics(engine, user_id, start_date=start_date, end_date=end_date)
    category_df = get_category_breakdown(engine, user_id, start_date=start_date, end_date=end_date)
    merchants_df = get_top_merchants(engine, user_id, start_date=start_date, end_date=end_date)

    budget_month = end_date.replace(day=1)
    budget_df = get_budget_vs_actual(engine, user_id, year=budget_month.year, month=budget_month.month)

    txn_df = get_transactions_for_recurring_check(engine, user_id)
    recurring = detect_recurring(txn_df)

    return ReportData(
        start_date=start_date,
        end_date=end_date,
        summary=summary,
        category_breakdown=category_df,
        top_merchants=merchants_df,
        budget_vs_actual=budget_df,
        budget_month=budget_month,
        recurring_payments=recurring,
    )