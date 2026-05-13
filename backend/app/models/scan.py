# backend/app/models/scan.py
"""
The Scan model represents a single repository analysis request.

Each row tracks the lifecycle of one scan from submission to completion:
created -> pending -> running -> completed (or failed).

We use an enum for status so the database enforces valid values - no chance
of a typo like "compleeted" sneaking in and breaking dashboards downstream.
"""
import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class ScanStatus(str, enum.Enum):
    """
    Lifecycle states a scan can be in. Inheriting from str makes these
    JSON-serializable out of the box - FastAPI will return "pending"
    rather than "ScanStatus.pending" in responses.
    """
    PENDING = "pending"      # In the queue, waiting for a worker
    RUNNING = "running"      # Worker has picked it up, cloning/scanning in progress
    COMPLETED = "completed"  # Scan finished successfully
    FAILED = "failed"        # Something went wrong - check error_message


class Scan(Base):
    """
    A single repo scan. Lives in the `scans` table in Postgres.

    We use UUID primary keys instead of auto-incrementing integers because:
    - They don't leak how many scans we've done (security through obscurity, but still)
    - They can be generated client-side or server-side, useful for distributed systems
    - They're globally unique - no collisions if we ever shard the DB
    """
    __tablename__ = "scans"

    # Primary key as UUID. Generated automatically when a row is created.
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # The repo URL we were asked to scan. Indexed because we'll likely
    # query "show me all scans of this repo" at some point.
    repo_url = Column(String(500), nullable=False, index=True)

    # Current lifecycle state. Defaults to PENDING when the row is first created.
    status = Column(
        Enum(ScanStatus, name="scan_status"),
        nullable=False,
        default=ScanStatus.PENDING,
        index=True,
    )

    # If status == FAILED, this holds the human-readable reason.
    # NULL for everything else.
    error_message = Column(Text, nullable=True)

    # Audit timestamps. Always use timezone-aware UTC times in databases -
    # naive datetimes will bite you when your team or servers cross timezones.
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        """Useful for debug logs: shows scan ID and status at a glance."""
        return f"<Scan id={self.id} status={self.status.value} url={self.repo_url}>"