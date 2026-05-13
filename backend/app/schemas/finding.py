# backend/app/schemas/finding.py
"""Pydantic schemas for the findings API."""
import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict

from app.models.finding import FindingType, Severity


class FindingResponse(BaseModel):
    """One finding as returned by the API. Mirrors the DB columns 1:1."""
    id: uuid.UUID
    scan_id: uuid.UUID
    finding_type: FindingType
    severity: Severity
    package_name: Optional[str] = None
    package_version: Optional[str] = None
    package_ecosystem: Optional[str] = None
    manifest_path: Optional[str] = None
    message: str
    extra_data: Optional[dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)