# backend/app/models/__init__.py
# Re-export models so `from app.models import Scan` works from anywhere.
# Also ensures models get registered with SQLAlchemy's metadata so
# create_all() in main.py knows to create their tables.

from app.models.scan import Scan, ScanStatus

__all__ = ["Scan", "ScanStatus"]