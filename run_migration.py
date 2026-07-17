from src.db.connection import engine
from sqlalchemy import text

with open("schema_migrations/002_add_users.sql", "r") as f:
    sql = f.read()

statements = [s.strip() for s in sql.split(";") if s.strip()]

with engine.connect() as conn:
    for stmt in statements:
        print(f"Running: {stmt[:60]}...")
        conn.execute(text(stmt))
    conn.commit()

print("Migration committed.")