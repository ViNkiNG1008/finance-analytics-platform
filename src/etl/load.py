"""
Load: write a cleaned & categorized DataFrame into PostgreSQL.
Now scoped per-user: every fact_transactions row is tagged with user_id.
"""
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session


def _upsert_date(session: Session, date: pd.Timestamp) -> None:
    session.execute(
        text("""
            INSERT INTO dim_date (date_id, day, month, month_name, quarter, year, day_of_week, is_weekend)
            VALUES (:date_id, :day, :month, :month_name, :quarter, :year, :day_of_week, :is_weekend)
            ON CONFLICT (date_id) DO NOTHING
        """),
        {
            "date_id": date.date(),
            "day": date.day,
            "month": date.month,
            "month_name": date.strftime("%B"),
            "quarter": (date.month - 1) // 3 + 1,
            "year": date.year,
            "day_of_week": date.strftime("%A"),
            "is_weekend": date.weekday() >= 5,
        },
    )


def _upsert_category(session: Session, category_name: str, category_type: str) -> int:
    session.execute(
        text("""
            INSERT INTO dim_category (category_name, category_type)
            VALUES (:name, :type)
            ON CONFLICT (category_name) DO NOTHING
        """),
        {"name": category_name, "type": category_type},
    )
    result = session.execute(
        text("SELECT category_id FROM dim_category WHERE category_name = :name"),
        {"name": category_name},
    )
    return result.scalar_one()


def _upsert_merchant(session: Session, merchant_name: str, default_category_id: int) -> int:
    session.execute(
        text("""
            INSERT INTO dim_merchant (merchant_name, default_category_id)
            VALUES (:name, :cat_id)
            ON CONFLICT (merchant_name) DO NOTHING
        """),
        {"name": merchant_name, "cat_id": default_category_id},
    )
    result = session.execute(
        text("SELECT merchant_id FROM dim_merchant WHERE merchant_name = :name"),
        {"name": merchant_name},
    )
    return result.scalar_one()


def _transaction_exists(session: Session, date_id, description: str, amount: float, user_id: int) -> bool:
    result = session.execute(
        text("""
            SELECT 1 FROM fact_transactions
            WHERE date_id = :date_id AND description = :description
              AND amount = :amount AND user_id = :user_id
            LIMIT 1
        """),
        {"date_id": date_id, "description": description, "amount": amount, "user_id": user_id},
    )
    return result.first() is not None


def load_transactions(df: pd.DataFrame, session: Session, source_file: str, user_id: int) -> int:
    """
    Load a cleaned & categorized DataFrame into fact_transactions,
    upserting dimension rows as needed. Dedup and rows are scoped to user_id
    so two users can independently upload statements with overlapping data
    without colliding.

    Args:
        df: DataFrame with columns
            ['date', 'description', 'merchant', 'category', 'amount', 'transaction_type']
        session: active SQLAlchemy session
        source_file: name of the originating statement file (for traceability)
        user_id: the logged-in user's id (from st.session_state["user_id"])

    Returns:
        Number of new rows inserted (rows already present for this user are skipped).
    """
    if user_id is None:
        raise ValueError("load_transactions requires a user_id — user must be logged in.")

    inserted = 0

    for _, row in df.iterrows():
        date = row["date"]
        date_id = date.date()

        if _transaction_exists(session, date_id, row["description"], row["amount"], user_id):
            continue  # already loaded this exact transaction for this user

        _upsert_date(session, date)

        category_type = "Income" if row["transaction_type"] == "Income" else "Expense"
        category_id = _upsert_category(session, row["category"], category_type)
        merchant_id = _upsert_merchant(session, row["merchant"], category_id)

        session.execute(
            text("""
                INSERT INTO fact_transactions
                    (date_id, merchant_id, category_id, description, amount, transaction_type, source_file, user_id)
                VALUES
                    (:date_id, :merchant_id, :category_id, :description, :amount, :transaction_type, :source_file, :user_id)
            """),
            {
                "date_id": date_id,
                "merchant_id": merchant_id,
                "category_id": category_id,
                "description": row["description"],
                "amount": row["amount"],
                "transaction_type": row["transaction_type"],
                "source_file": source_file,
                "user_id": user_id,
            },
        )
        inserted += 1

    session.commit()
    return inserted