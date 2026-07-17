from src.db.connection import engine
from sqlalchemy import text

query = """
SELECT table_name, column_name
FROM information_schema.columns
WHERE table_name IN ('fact_transactions', 'budgets', 'users')
ORDER BY table_name, column_name
"""

with engine.connect() as conn:
    result = conn.execute(text(query))
    for row in result:
        print(row)