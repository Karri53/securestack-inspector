# backend/app/main.py
"""
FastAPI application entrypoint. This is the file uvicorn loads.

Phase 2 additions:
- Auto-creates DB tables from SQLAlchemy models on startup (no Alembic yet -
  we'll introduce migrations in a later phase when we need to evolve the schema)
- Mounts the scans router under /api/scans
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api import scans
from app.core.config import settings
from app.core.database import Base, engine

# Importing models here ensures they get registered with Base.metadata
# BEFORE we call create_all(). Without this import, SQLAlchemy doesn't
# know the tables exist and silently creates nothing.
from app.models import scan as scan_model  # noqa: F401

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SecureStack Inspector",
    description="Containerized software supply chain risk analyzer",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the scans router. All its routes will be under /api/scans/...
app.include_router(scans.router)


@app.on_event("startup")
def on_startup():
    """
    Boots the app. Runs once at startup.

    create_all() is idempotent - it only creates tables that don't exist yet.
    Safe to run on every startup. We'll swap this for Alembic migrations
    once the schema starts changing in non-trivial ways.
    """
    logger.info("SecureStack Inspector API starting in %s mode", settings.api_env)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified")


@app.get("/", tags=["system"])
def root():
    return {
        "service": "SecureStack Inspector API",
        "version": "0.2.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["system"])
def health():
    """Liveness + readiness probe. Same as Phase 1."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        logger.exception("Database health check failed")
        db_status = f"error: {e}"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "service": "securestack-api",
        "version": "0.2.0",
        "database": db_status,
    }