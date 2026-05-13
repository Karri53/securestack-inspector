# backend/app/schemas/scan.py
"""
Pydantic schemas for the scans API.

These define the SHAPE of requests and responses. They're separate from the
SQLAlchemy models in app/models/ because the API contract should be free to
evolve independently from the database schema.
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from app.models.scan import ScanStatus


class ScanCreate(BaseModel):
    """
    Request body for POST /api/scans.

    Pydantic + HttpUrl gives us free URL validation: malformed URLs return
    a 422 error before our code ever runs. We add a custom validator to
    restrict to public GitHub URLs - allowing arbitrary URLs would let
    someone trick the worker into cloning from internal services (SSRF).
    """
    repo_url: HttpUrl = Field(
        ...,
        description="Public GitHub repository URL to scan",
        examples=["https://github.com/octocat/Hello-World"],
    )

    @field_validator("repo_url")
    @classmethod
    def must_be_github(cls, v: HttpUrl) -> HttpUrl:
        """
        Reject anything that isn't github.com. Future phases can expand
        to GitLab/Bitbucket; for now keeping the attack surface small.
        """
        host = v.host or ""
        if host.lower() not in ("github.com", "www.github.com"):
            raise ValueError("Only github.com URLs are supported in Phase 2")
        return v


class ScanResponse(BaseModel):
    """
    Response body returned by every scans endpoint.

    Pydantic v2's model_config + from_attributes=True lets us pass a
    SQLAlchemy Scan instance directly and Pydantic will pull out the
    matching attributes. No manual dict-building needed.
    """
    id: uuid.UUID
    repo_url: str
    status: ScanStatus
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)