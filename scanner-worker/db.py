# scanner-worker/db.py
"""
Standalone DB engine for the worker process.

This is intentionally a separate file from backend/app/core/database.py.
The worker is a different deployable - separate codebase, separate dependencies,
separate process. Sharing code by symlinking or volume mounts would couple
deployments in ways we don't want. Small duplication is the right tradeoff here.
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def _build_database_url() -> str:
    """Pull connection params from env and assemble the SQLAlchemy URL."""
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    host = os.environ["POSTGRES_HOST"]
    port = os.environ["POSTGRES_PORT"]
    db = os.environ["POSTGRES_DB"]
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


# Module-level engine + session factory. Workers run as long-lived processes,
# so opening these once at import and reusing them is the right pattern.
engine = create_engine(_build_database_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)