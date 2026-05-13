# backend/app/models/__init__.py
# Re-export models so `from app.models import X` works from anywhere.
# Also ensures models get registered with SQLAlchemy's metadata before
# create_all() runs - missing imports here = missing tables.

from app.models.finding import Finding, FindingType, Severity
from app.models.scan import Scan, ScanStatus

__all__ = ["Scan", "ScanStatus", "Finding", "FindingType", "Severity"]