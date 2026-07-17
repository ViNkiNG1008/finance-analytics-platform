"""
SQLAlchemy engine + session factory for the Postgres database.
Used by the ETL loader and the Streamlit app.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"sslmode": "require"},
    use_native_hstore=False,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_session():
    """Yield a DB session; caller is responsible for closing it."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()