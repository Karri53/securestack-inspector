# backend/app/models/finding.py
"""
The Finding model represents one specific issue or observation surfaced
by a scan. In Phase 3 these are inventory items: "we found package X at
version Y in this manifest." Later phases will add Dockerfile findings,
SBOM entries, and vulnerability matches.

Keeping all finding types in a single table (with a `finding_type` enum
to discriminate) keeps queries simple - one "show me everything bad about
this repo" query, not five separate joins.
"""
import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class FindingType(str, enum.Enum):
    """What KIND of finding this is. Phase 3 only emits DEPENDENCY."""
    DEPENDENCY = "dependency"        # Phase 3: inventory of packages
    DOCKERFILE_ISSUE = "dockerfile"  # Phase 4
    SBOM_ENTRY = "sbom"              # Phase 5
    VULNERABILITY = "vulnerability"  # later


class Severity(str, enum.Enum):
    """
    Standard 5-level severity. Aligned with CVSS qualitative ratings so
    later phases can map CVE scores directly into these buckets.

    For pure inventory findings (Phase 3), everything is INFO - we haven't
    judged anything yet. Phase 4+ will elevate severity based on CVE matches.
    """
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Finding(Base):
    __tablename__ = "findings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # FK to the parent scan. ON DELETE CASCADE means deleting a scan
    # automatically cleans up its findings - no orphan rows.
    scan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("scans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    finding_type = Column(Enum(FindingType, name="finding_type"), nullable=False, index=True)
    severity = Column(Enum(Severity, name="severity"), nullable=False, default=Severity.INFO, index=True)

    # ---- Dependency-specific fields ----
    # These are NULL for non-DEPENDENCY findings. Putting them inline (rather
    # than a separate dependencies table) keeps queries simple for Phase 3.
    # If finding types diverge significantly later, we'll split this up.
    package_name = Column(String(255), nullable=True, index=True)
    package_version = Column(String(255), nullable=True)
    package_ecosystem = Column(String(50), nullable=True)  # "pypi", "npm", etc.

    # Where in the repo we found it. Relative path from the repo root.
    manifest_path = Column(String(500), nullable=True)

    # Human-readable description. Required - every finding needs a message.
    message = Column(Text, nullable=False)

    # Free-form structured data for things that don't fit the columns above.
    # JSONB is Postgres-specific but worth it - indexed JSON queries are fast.
    extra_data = Column(JSONB, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Convenience relationship for ORM queries (Scan.findings)
    scan = relationship("Scan", backref="findings")

    def __repr__(self) -> str:
        return f"<Finding id={self.id} type={self.finding_type.value} pkg={self.package_name}>"