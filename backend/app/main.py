# backend/app/main.py
"""
FastAPI application entrypoint. This is the file uvicorn loads.

For Phase 1 we only have system endpoints (/, /health). Real scan endpoints
come in Phase 2.
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine

# Set up logging once at the entrypoint. Every other module just does
# `logger = logging.getLogger(__name__)` and picks up this config.
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SecureStack Inspector",
    description="Containerized software supply chain risk analyzer",
    version="0.1.0",
)

# CORS: the frontend runs on http://localhost:3000 in the browser, and the
# API runs on http://localhost:8000. Without CORS, the browser blocks
# cross-origin requests. In production we'd lock this down to specific
# origins, not "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Runs once when uvicorn boots. Good place to log environment info."""
    logger.info("SecureStack Inspector API starting in %s mode", settings.api_env)


@app.get("/", tags=["system"])
def root():
    """Friendly landing endpoint for humans hitting the root URL."""
    return {
        "service": "SecureStack Inspector API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["system"])
def health():
    """
    Liveness + readiness probe.

    Returns 200 with database status. This is what Docker's HEALTHCHECK
    in the Dockerfile pings, and what Kubernetes readiness probes would hit
    if/when we deploy there.

    "Degraded" means the API is alive but can't reach Postgres — useful
    distinction for ops dashboards.
    """
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
        "version": "0.1.0",
        "database": db_status,
    }