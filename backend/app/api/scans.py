# backend/app/api/scans.py
"""
REST endpoints for the scans resource.

Routing pattern:
- POST   /api/scans       - submit a new scan
- GET    /api/scans       - list scans (most recent first)
- GET    /api/scans/{id}  - fetch one scan's status

We follow REST conventions where they're useful, but we also enqueue a
Redis job inside the POST handler - the API is the publisher, the worker
is the subscriber, and Postgres is the source of truth either side reads from.
"""
import json
import logging
import uuid

import redis
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.scan import Scan, ScanStatus
from app.schemas.scan import ScanCreate, ScanResponse

logger = logging.getLogger(__name__)

# The router gets mounted under /api in main.py, so paths here are relative.
router = APIRouter(prefix="/api/scans", tags=["scans"])

# Redis queue name. The worker pops from this same key.
# Keeping it as a module-level constant means we change it in one place if needed.
QUEUE_KEY = "scans:queue"


def get_redis() -> redis.Redis:
    """
    FastAPI dependency that returns a Redis client.

    Building it per-request is fine - redis-py uses an internal connection pool,
    so this isn't actually opening a new TCP connection every time.
    decode_responses=True makes Redis return strings instead of bytes.
    """
    return redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        decode_responses=True,
    )


@router.post(
    "",
    response_model=ScanResponse,
    status_code=status.HTTP_202_ACCEPTED,  # 202 = "accepted, will process asynchronously"
)
def create_scan(
    payload: ScanCreate,
    db: Session = Depends(get_db),
    r: redis.Redis = Depends(get_redis),
):
    """
    Submit a new scan.

    The flow:
    1. Create a Scan row in Postgres (status=pending)
    2. Push a job onto the Redis queue with the scan_id
    3. Return the scan record to the client

    The worker handles everything from here. 202 Accepted is the right code
    here - we've taken responsibility for the work but haven't done it yet.
    """
    # Pydantic gave us a validated HttpUrl; convert to string for storage
    repo_url_str = str(payload.repo_url)

    # Create the row. The DB defaults handle id, status, and timestamps.
    scan = Scan(repo_url=repo_url_str)
    db.add(scan)
    db.commit()
    db.refresh(scan)  # Reloads the row so we get the DB-generated id

    # Enqueue. JSON-encoding the payload means we can easily evolve the
    # message format later (add scan options, priorities, etc.) without
    # breaking the wire format.
    job = json.dumps({
        "scan_id": str(scan.id),
        "repo_url": repo_url_str,
    })
    r.lpush(QUEUE_KEY, job)

    logger.info("Enqueued scan %s for %s", scan.id, repo_url_str)
    return scan


@router.get("", response_model=list[ScanResponse])
def list_scans(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    List scans, most recent first.

    Default limit of 20 keeps responses snappy. ge/le constraints prevent
    a client from passing limit=999999 and DOS-ing us.
    """
    scans = (
        db.query(Scan)
        .order_by(desc(Scan.created_at))
        .limit(limit)
        .all()
    )
    return scans


@router.get("/{scan_id}", response_model=ScanResponse)
def get_scan(scan_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Fetch a single scan by ID. 404 if it doesn't exist.

    Typing scan_id as UUID gives us automatic validation - if someone
    passes "not-a-uuid", FastAPI returns 422 before we ever query the DB.
    """
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan {scan_id} not found",
        )
    return scan