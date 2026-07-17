"""
Analytics queries for the Streamlit dashboard (Phase 5).
Every function takes a SQLAlchemy Engine + user_id and returns a pandas
DataFrame (or a plain dict/int for scalar results) — no SQLAlchemy objects
leak into the Streamlit pages.

All fact_transactions/budgets queries are now scoped by user_id so each
logged-in user only ever sees their own data.

Sign convention (per schema.sql): amount is positive for Income,
negative for Expense. Expense totals below are reported as positive
magnitudes (ABS) since that's what a dashboard user expects to read.
"""
from typing import Optional, Sequence

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine


# ---------------------------------------------------------------------
# Dashboard summary + trends
# ---------------------------------------------------------------------

def get_summary_metrics(engine: Engine, user_id: int, start_date=None, end_date=None) -> dict:
    """Total income, total expense, net savings, savings rate — for one user."""
    clauses = ["user_id = :user_id"]
    params = {"user_id": user_id}
    if start_date:
        clauses.append("date_id >= :start_date")
        params["start_date"] = start_date
    if end_date:
        clauses.append("date_id <= :end_date")
        params["end_date"] = end_date
    where_sql = f"WHERE {' AND '.join(clauses)}"

    query = text(f"""
        SELECT transaction_type, COALESCE(SUM(amount), 0) AS total
        FROM fact_transactions
        {where_sql}
        GROUP BY transaction_type
    """)
    with engine.connect() as conn:
        rows = conn.execute(query, params).fetchall()

    totals = {row.transaction_type: float(row.total) for row in rows}
    income = totals.get("Income", 0.0)
    expense = abs(totals.get("Expense", 0.0))
    net_savings = income - expense
    savings_rate = (net_savings / income * 100) if income > 0 else 0.0

    return {
        "total_income": income,
        "total_expense": expense,
        "net_savings": net_savings,
        "savings_rate": savings_rate,
    }


def get_category_breakdown(engine: Engine, user_id: int, start_date=None, end_date=None) -> pd.DataFrame:
    """Expense total per category for one user — feeds the donut chart."""
    clauses = ["f.transaction_type = 'Expense'", "f.user_id = :user_id"]
    params = {"user_id": user_id}
    if start_date:
        clauses.append("f.date_id >= :start_date")
        params["start_date"] = start_date
    if end_date:
        clauses.append("f.date_id <= :end_date")
        params["end_date"] = end_date
    where_sql = "WHERE " + " AND ".join(clauses)

    query = text(f"""
        SELECT c.category_name, SUM(ABS(f.amount)) AS total
        FROM fact_transactions f
        JOIN dim_category c ON f.category_id = c.category_id
        {where_sql}
        GROUP BY c.category_name
        ORDER BY total DESC
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params=params)
    return df


def get_monthly_trend(engine: Engine, user_id: int, months: int = 12) -> pd.DataFrame:
    """
    Income vs Expense per month for the last N months, for one user.
    Returns columns: month (Timestamp), income, expense (both positive numbers).
    """
    query = text("""
        SELECT date_trunc('month', date_id)::date AS month,
               transaction_type,
               SUM(amount) AS total
        FROM fact_transactions
        WHERE date_id >= (CURRENT_DATE - (:months || ' months')::interval)
          AND user_id = :user_id
        GROUP BY 1, 2
        ORDER BY 1
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"months": months, "user_id": user_id})

    if df.empty:
        return pd.DataFrame(columns=["month", "income", "expense"])

    pivot = df.pivot(index="month", columns="transaction_type", values="total").fillna(0)
    pivot = pivot.rename(columns={"Income": "income", "Expense": "expense"})
    if "income" not in pivot:
        pivot["income"] = 0.0
    if "expense" not in pivot:
        pivot["expense"] = 0.0
    pivot["expense"] = pivot["expense"].abs()
    pivot = pivot.reset_index()
    return pivot[["month", "income", "expense"]]


def get_top_merchants(engine: Engine, user_id: int, start_date=None, end_date=None, limit: int = 10) -> pd.DataFrame:
    """Top merchants by total spend for one user — feeds the 'top merchants' bar chart."""
    clauses = ["f.transaction_type = 'Expense'", "f.user_id = :user_id"]
    params = {"user_id": user_id, "limit": limit}
    if start_date:
        clauses.append("f.date_id >= :start_date")
        params["start_date"] = start_date
    if end_date:
        clauses.append("f.date_id <= :end_date")
        params["end_date"] = end_date
    where_sql = "WHERE " + " AND ".join(clauses)

    query = text(f"""
        SELECT m.merchant_name, SUM(ABS(f.amount)) AS total_spent, COUNT(*) AS txn_count
        FROM fact_transactions f
        JOIN dim_merchant m ON f.merchant_id = m.merchant_id
        {where_sql}
        GROUP BY m.merchant_name
        ORDER BY total_spent DESC
        LIMIT :limit
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params=params)
    return df


# ---------------------------------------------------------------------
# Transactions page
# ---------------------------------------------------------------------

def get_transactions(
    engine: Engine,
    user_id: int,
    search: Optional[str] = None,
    categories: Optional[Sequence[str]] = None,
    start_date=None,
    end_date=None,
    limit: int = 1000,
) -> pd.DataFrame:
    """Filtered transaction list for one user, most recent first."""
    clauses = ["f.user_id = :user_id"]
    params = {"user_id": user_id, "limit": limit}

    if search:
        clauses.append("(f.description ILIKE :search OR m.merchant_name ILIKE :search)")
        params["search"] = f"%{search}%"
    if categories:
        clauses.append("c.category_name = ANY(:categories)")
        params["categories"] = list(categories)
    if start_date:
        clauses.append("f.date_id >= :start_date")
        params["start_date"] = start_date
    if end_date:
        clauses.append("f.date_id <= :end_date")
        params["end_date"] = end_date

    where_sql = f"WHERE {' AND '.join(clauses)}"

    query = text(f"""
        SELECT f.date_id AS date,
               m.merchant_name AS merchant,
               c.category_name AS category,
               f.amount,
               f.transaction_type,
               f.description
        FROM fact_transactions f
        LEFT JOIN dim_merchant m ON f.merchant_id = m.merchant_id
        LEFT JOIN dim_category c ON f.category_id = c.category_id
        {where_sql}
        ORDER BY f.date_id DESC, f.transaction_id DESC
        LIMIT :limit
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params=params)
    return df


# ---------------------------------------------------------------------
# Budget page
# ---------------------------------------------------------------------

def get_expense_categories(engine: Engine) -> pd.DataFrame:
    """All expense categories, for populating the budget-editing widgets.
    Categories are shared/global, so no user_id filter here."""
    query = text("""
        SELECT category_id, category_name
        FROM dim_category
        WHERE category_type = 'Expense'
        ORDER BY category_name
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df


def get_budget_vs_actual(engine: Engine, user_id: int, year: int, month: int) -> pd.DataFrame:
    """
    Budgeted limit vs actual spend per expense category for a given month,
    scoped to one user. Categories with no budget row yet show monthly_limit = 0.
    """
    query = text("""
        SELECT
            c.category_id,
            c.category_name,
            COALESCE(b.monthly_limit, 0) AS monthly_limit,
            COALESCE(actual.spent, 0) AS actual_spent
        FROM dim_category c
        LEFT JOIN budgets b ON b.category_id = c.category_id AND b.user_id = :user_id
        LEFT JOIN (
            SELECT category_id, SUM(ABS(amount)) AS spent
            FROM fact_transactions
            WHERE transaction_type = 'Expense'
              AND user_id = :user_id
              AND EXTRACT(YEAR FROM date_id) = :year
              AND EXTRACT(MONTH FROM date_id) = :month
            GROUP BY category_id
        ) actual ON actual.category_id = c.category_id
        WHERE c.category_type = 'Expense'
        ORDER BY c.category_name
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"user_id": user_id, "year": year, "month": month})
    return df


def upsert_budget(engine: Engine, user_id: int, category_id: int, monthly_limit: float) -> None:
    """Set (or update) the monthly budget limit for a category, for one user."""
    query = text("""
        INSERT INTO budgets (category_id, monthly_limit, user_id)
        VALUES (:category_id, :monthly_limit, :user_id)
        ON CONFLICT (category_id, user_id)
        DO UPDATE SET monthly_limit = EXCLUDED.monthly_limit
    """)
    with engine.begin() as conn:
        conn.execute(query, {"category_id": category_id, "monthly_limit": monthly_limit, "user_id": user_id})


def get_transactions_for_recurring_check(engine: Engine, user_id: int) -> pd.DataFrame:
    """Pulls expense transactions with merchant/category for recurring detection, for one user."""
    query = text("""
        SELECT
            f.merchant_id,
            m.merchant_name,
            c.category_name,
            f.amount,
            d.date_id AS txn_date
        FROM fact_transactions f
        JOIN dim_merchant m ON f.merchant_id = m.merchant_id
        JOIN dim_category c ON f.category_id = c.category_id
        JOIN dim_date d ON f.date_id = d.date_id
        WHERE f.amount < 0 AND f.user_id = :user_id
        ORDER BY f.merchant_id, d.date_id
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"user_id": user_id})
    return df