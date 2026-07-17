"""One-off: list tables in the connected database, with diagnostics."""
from sqlalchemy import text
from src.db.connection import engine
from config.settings import settings

print(f"Connecting to: {settings.db_host}/{settings.db_name} as {settings.db_user}")

try:
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
        ).fetchall()
    print(f"Found {len(rows)} table(s):")
    for row in rows:
        print(" -", row[0])
except Exception as e:
    print("ERROR:", repr(e))