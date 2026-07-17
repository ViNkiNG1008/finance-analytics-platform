from src.db.connection import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT user_id, username, email FROM users"))
    for row in result:
        print(row)