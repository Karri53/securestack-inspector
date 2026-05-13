# backend/app/core/database.py
"""
SQLAlchemy 2.0 engine and session machinery.

Engine = the connection pool. Built once at app startup, reused for every request.
Session = a unit of work — opened per-request, closed when the request ends.
Base    = the class all ORM models inherit from.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# pool_pre_ping=True makes SQLAlchemy verify each connection is still alive
# before handing it out. Without this, you eventually hit "connection closed"
# errors after Postgres restarts or network blips. Cheap insurance.
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=False,  # Flip to True locally to see every SQL query — invaluable for debugging
)

# Session factory. Don't call this directly in route handlers — use the
# get_db() dependency below so cleanup is guaranteed.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for every ORM model. SQLAlchemy 2.0 style."""
    pass


def get_db():
    """
    FastAPI dependency. Yields a DB session and guarantees it gets closed
    even if the request raises an exception.

    Use like:
        @app.get("/scans")
        def list_scans(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()