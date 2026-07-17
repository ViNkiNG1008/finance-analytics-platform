"""
Centralized configuration. Loads from .env locally, or from Streamlit
Cloud's st.secrets when deployed. No secrets live in code.
Import `settings` anywhere in the app: `from config.settings import settings`
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

# On Streamlit Cloud, values live in st.secrets, not os.environ.
# Pull them into os.environ (only if not already set locally) so the
# rest of this file — and any non-Streamlit script like run_migration.py —
# keeps working unchanged.
try:
    import streamlit as st
    if hasattr(st, "secrets"):
        for _key in ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD", "APP_ENV"):
            if _key in st.secrets and not os.getenv(_key):
                os.environ[_key] = str(st.secrets[_key])
except Exception:
    # Not running inside Streamlit, or no secrets.toml present (e.g. local
    # scripts / migrations) — fall back to .env / os.environ as before.
    pass


@dataclass(frozen=True)
class Settings:
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: str = os.getenv("DB_PORT", "5432")
    db_name: str = os.getenv("DB_NAME", "finance_db")
    db_user: str = os.getenv("DB_USER", "finance_user")
    db_password: str = os.getenv("DB_PASSWORD", "")
    app_env: str = os.getenv("APP_ENV", "development")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()