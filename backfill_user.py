from src.db.connection import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(
        text("UPDATE fact_transactions SET user_id = :uid WHERE user_id IS NULL"),
        {"uid": 2},
    )
    print(f"Updated {result.rowcount} transaction rows.")
    conn.commit()