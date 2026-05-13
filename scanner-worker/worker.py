# scanner-worker/worker.py
"""
The scanner worker. Phase 3: pulls jobs, clones repos, runs analyzers,
persists findings.

Pipeline per job:
  1. Mark scan as RUNNING
  2. Clone the repo (Phase 2)
  3. Run dependency scanner against the clone (Phase 3)
  4. Persist findings to DB
  5. Mark scan as COMPLETED (or FAILED)
"""
import enum
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List

import redis
from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase

from db import SessionLocal
from scanners.clone import CloneError, clone_repo
from scanners.dependencies.base import ParsedPackage
from scanners.dependencies.walker import scan_dependencies

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] worker: %(message)s",
)
logger = logging.getLogger(__name__)

QUEUE_KEY = "scans:queue"


# ----------------------------------------------------------------------
# DB models mirrored from backend. Must stay in sync with backend/app/models/.
# ----------------------------------------------------------------------
class ScanStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class FindingType(str, enum.Enum):
    DEPENDENCY = "dependency"
    DOCKERFILE_ISSUE = "dockerfile"
    SBOM_ENTRY = "sbom"
    VULNERABILITY = "vulnerability"


class Severity(str, enum.Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Base(DeclarativeBase):
    pass


class Scan(Base):
    __tablename__ = "scans"
    id = Column(UUID(as_uuid=True), primary_key=True)
    repo_url = Column(String(500), nullable=False)
    status = Column(SQLEnum(ScanStatus, name="scan_status"), nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)


class Finding(Base):
    __tablename__ = "findings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    finding_type = Column(SQLEnum(FindingType, name="finding_type"), nullable=False)
    severity = Column(SQLEnum(Severity, name="severity"), nullable=False)
    package_name = Column(String(255), nullable=True)
    package_version = Column(String(255), nullable=True)
    package_ecosystem = Column(String(50), nullable=True)
    manifest_path = Column(String(500), nullable=True)
    message = Column(Text, nullable=False)
    extra_data = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


# ----------------------------------------------------------------------
# DB helpers
# ----------------------------------------------------------------------
def update_scan(scan_id: uuid.UUID, **updates) -> None:
    """Update a scan row. Always sets updated_at to now."""
    updates["updated_at"] = datetime.now(timezone.utc)
    with SessionLocal() as session:
        session.query(Scan).filter(Scan.id == scan_id).update(updates)
        session.commit()


def persist_findings(scan_id: uuid.UUID, packages: List[ParsedPackage]) -> int:
    """
    Bulk-insert one Finding row per ParsedPackage. Returns the count inserted.

    Uses add_all + commit rather than individual inserts - one round trip
    to the DB regardless of how many packages there are. Big repos can have
    hundreds of deps; individual inserts would be slow.
    """
    if not packages:
        return 0

    findings = [
        Finding(
            scan_id=scan_id,
            finding_type=FindingType.DEPENDENCY,
            severity=Severity.INFO,  # Pure inventory in Phase 3 - no judgment yet
            package_name=pkg.name,
            package_version=pkg.version,
            package_ecosystem=pkg.ecosystem,
            manifest_path=pkg.manifest_path,
            message=f"Dependency: {pkg.name}" + (f" ({pkg.version})" if pkg.version else ""),
        )
        for pkg in packages
    ]

    with SessionLocal() as session:
        session.add_all(findings)
        session.commit()

    return len(findings)


# ----------------------------------------------------------------------
# Main job processor
# ----------------------------------------------------------------------
def process_job(payload: dict) -> None:
    """
    Handle one scan job end to end:
        clone -> analyze -> persist findings -> mark complete

    Exceptions never propagate. The loop must survive any single job failing.
    """
    scan_id = uuid.UUID(payload["scan_id"])
    repo_url = payload["repo_url"]

    logger.info("Processing scan %s (%s)", scan_id, repo_url)
    update_scan(scan_id, status=ScanStatus.RUNNING)

    try:
        # Phase 2: clone
        repo_path = clone_repo(str(scan_id), repo_url)

        # Phase 3: walk the clone, parse manifests, persist findings
        packages = scan_dependencies(Path(repo_path))
        count = persist_findings(scan_id, packages)
        logger.info("Scan %s persisted %d dependency findings", scan_id, count)

        # Future phases will add more analyzers (Dockerfile linter, SBOM, ...)
        # before this completion line. Each one appends to the findings table.

        update_scan(scan_id, status=ScanStatus.COMPLETED, error_message=None)
        logger.info("Scan %s completed", scan_id)
    except CloneError as e:
        logger.error("Scan %s failed at clone: %s", scan_id, e)
        update_scan(scan_id, status=ScanStatus.FAILED, error_message=str(e))
    except Exception as e:
        logger.exception("Scan %s crashed unexpectedly", scan_id)
        update_scan(scan_id, status=ScanStatus.FAILED, error_message=f"Internal error: {e}")


def main():
    redis_host = os.environ["REDIS_HOST"]
    redis_port = int(os.environ["REDIS_PORT"])

    logger.info("Connecting to Redis at %s:%s", redis_host, redis_port)
    r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    r.ping()
    logger.info("Worker ready. Polling %s for jobs...", QUEUE_KEY)

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
            logger.exception("Unhandled error in main loop")


if __name__ == "__main__":
    main()