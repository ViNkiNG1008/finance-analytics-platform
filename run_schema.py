"""One-off: apply src/db/schema.sql against the configured database."""
from pathlib import Path
from sqlalchemy import text
from src.db.connection import engine

sql = Path("src/db/schema.sql").read_text(encoding="utf-8")

with engine.begin() as conn:
    conn.execute(text(sql))

print("Schema applied successfully.")
