# scanner-worker/worker.py
"""
The scanner worker. Pulls jobs from Redis, clones repos, updates the DB.

Phase 2 scope: clone only. Phase 3 will add dependency parsing, Phase 4
Dockerfile linting, Phase 5 SBOM generation. Each phase plugs in here.

The main loop is intentionally simple: BLPOP, dispatch, repeat. No fancy
job framework (Celery, RQ) because we want full visibility into what the
worker does for the scope of this project. Adding Celery later is a
straightforward swap if we need features like retries or schedules.
"""
import json
import logging
import os
import uuid
from datetime import datetime, timezone

import redis
from sqlalchemy import Column, DateTime, Enum as SQLEnum, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase

from db import SessionLocal
from scanners.clone import CloneError, clone_repo

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] worker: %(message)s",
)
logger = logging.getLogger(__name__)

QUEUE_KEY = "scans:queue"

# The worker has its own copy of the Scan model. We could share with the
# backend, but that would couple deploys. Mirror the schema instead;
# Postgres is the source of truth either side reads from.
import enum


class ScanStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Base(DeclarativeBase):
    pass


class Scan(Base):
    """Mirror of backend's Scan model. Schema must match exactly."""
    __tablename__ = "scans"
    id = Column(UUID(as_uuid=True), primary_key=True)
    repo_url = Column(String(500), nullable=False)
    status = Column(SQLEnum(ScanStatus, name="scan_status"), nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)


def update_scan(scan_id: uuid.UUID, **updates) -> None:
    """
    Update a scan row in the DB. Always sets updated_at to now.

    Wrapped in its own function so the main loop reads cleanly: every
    state transition is a single line.
    """
    updates["updated_at"] = datetime.now(timezone.utc)
    with SessionLocal() as session:
        session.query(Scan).filter(Scan.id == scan_id).update(updates)
        session.commit()


def process_job(payload: dict) -> None:
    """
    Handle one scan job.

    On success: status flips to COMPLETED.
    On failure: status flips to FAILED with error_message populated.

    Exceptions never propagate out - the loop must keep running even if
    one job fails catastrophically. We log the full traceback for debugging.
    """
    scan_id = uuid.UUID(payload["scan_id"])
    repo_url = payload["repo_url"]

    logger.info("Processing scan %s (%s)", scan_id, repo_url)
    update_scan(scan_id, status=ScanStatus.RUNNING)

    try:
        clone_repo(str(scan_id), repo_url)
        # Phase 3+ will add: parse deps, lint Dockerfile, gen SBOM, score risk.
        # For now, successful clone = completed scan.
        update_scan(scan_id, status=ScanStatus.COMPLETED, error_message=None)
        logger.info("Scan %s completed", scan_id)
    except CloneError as e:
        logger.error("Scan %s failed: %s", scan_id, e)
        update_scan(scan_id, status=ScanStatus.FAILED, error_message=str(e))
    except Exception as e:
        # Catch-all so the worker never dies on an unexpected error
        logger.exception("Scan %s crashed unexpectedly", scan_id)
        update_scan(scan_id, status=ScanStatus.FAILED, error_message=f"Internal error: {e}")


def main():
    redis_host = os.environ["REDIS_HOST"]
    redis_port = int(os.environ["REDIS_PORT"])

    logger.info("Connecting to Redis at %s:%s", redis_host, redis_port)
    r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    r.ping()
    logger.info("Worker ready. Polling %s for jobs...", QUEUE_KEY)

    # BLPOP blocks until a job arrives (or `timeout` seconds elapse).
    # timeout=0 means block forever - the right behavior for a worker
    # that should idle quietly between jobs without busy-polling.
    while True:
        try:
            result = r.blpop(QUEUE_KEY, timeout=0)
            if result is None:
                continue
            _key, raw_payload = result
            payload = json.loads(raw_payload)
            process_job(payload)
        except json.JSONDecodeError:
            logger.error("Discarding malformed job: %r", raw_payload)
        except Exception:
            # Top-level safety net. Even if process_job somehow throws,
            # we log and keep looping.
            logger.exception("Unhandled error in main loop")


if __name__ == "__main__":
    main()