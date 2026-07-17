from src.db.connection import engine
from sqlalchemy import text

statements = [
    "ALTER TABLE budgets DROP CONSTRAINT IF EXISTS budgets_category_id_key;",
    "ALTER TABLE budgets ADD CONSTRAINT budgets_category_user_unique UNIQUE (category_id, user_id);",
]

with engine.connect() as conn:
    for stmt in statements:
        print(f"Running: {stmt}")
        conn.execute(text(stmt))
    conn.commit()

print("Constraint fix committed.")