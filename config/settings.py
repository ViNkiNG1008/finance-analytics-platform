"""
Centralized configuration. Loads from .env so no secrets live in code.
Import `settings` anywhere in the app: `from config.settings import settings`
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


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
