# scanner-worker/scanners/dependencies/base.py
"""
Shared types for dependency parsers.

Every parser returns a list of ParsedPackage objects. Keeping this dead simple -
just name, version, ecosystem, and where we found it - means new parsers
plug in trivially. Phase 4 can add CVE lookup by reading these.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedPackage:
    """One dependency found in a manifest file."""
    name: str
    version: Optional[str]      # The version SPECIFIER (e.g. ">=1.0,<2.0"), not a resolved version
    ecosystem: str              # "pypi", "npm", etc. - matches OSV/CVE database conventions
    manifest_path: str          # Relative path from repo root, e.g. "backend/requirements.txt"