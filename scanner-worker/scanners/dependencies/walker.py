# scanner-worker/scanners/dependencies/walker.py
"""
Walks a cloned repo, finds manifest files, dispatches each to the right parser.

Public API is just one function: scan_dependencies(repo_path).
Returns a flat list of every ParsedPackage found anywhere in the tree.
"""
import logging
from pathlib import Path
from typing import List

from .base import ParsedPackage
from .node import parse_package_json
from .python import parse_requirements_txt

logger = logging.getLogger(__name__)

# Directories we never walk into. node_modules can contain millions of files
# from transitive deps - we only care about the TOP-LEVEL package.json, not
# every nested one. Same logic for vendor/, .git/, etc.
SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "vendor", "dist", "build"}

# Map filename -> parser function. Adding a new ecosystem is now one line.
PARSERS = {
    "requirements.txt": parse_requirements_txt,
    "package.json": parse_package_json,
}


def scan_dependencies(repo_path: Path) -> List[ParsedPackage]:
    """
    Walk repo_path recursively, parse every recognized manifest, return all packages.

    Single repo can have multiple manifests (e.g., monorepo with frontend +
    backend), so we collect findings from all of them.
    """
    all_packages: List[ParsedPackage] = []

    # Path.rglob('*') would walk into node_modules. We do our own walk so
    # we can prune those directories before recursing into them.
    for path in _walk(repo_path):
        if path.name in PARSERS:
            parser = PARSERS[path.name]
            packages = parser(path, repo_path)
            all_packages.extend(packages)

    logger.info("Found %d total packages across all manifests", len(all_packages))
    return all_packages


def _walk(root: Path):
    """
    Yield every file under root, skipping directories in SKIP_DIRS.

    Implemented manually instead of using os.walk so the prune logic is obvious
    and the SKIP_DIRS check happens BEFORE descending (not after, which would
    still cost us a directory listing per skip).
    """
    if not root.is_dir():
        return
    try:
        for child in root.iterdir():
            if child.is_dir():
                if child.name in SKIP_DIRS:
                    continue
                yield from _walk(child)
            elif child.is_file():
                yield child
    except (OSError, PermissionError) as e:
        logger.warning("Skipping %s due to: %s", root, e)