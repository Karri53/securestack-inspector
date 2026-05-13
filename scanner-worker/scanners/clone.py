# scanner-worker/scanners/clone.py
"""
Git clone helper.

Clones the target repo into /workspace/<scan_id>/. The /workspace volume
is bind-mounted in docker-compose so it survives container restarts and
is inspectable from the host (great for debugging).

Phase 2 just clones - actual scanning happens in Phase 3+.
"""
import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

# Where cloned repos live. Each scan gets its own subdirectory keyed by ID.
WORKSPACE_ROOT = Path("/workspace")

# Hard timeout. Some repos are huge or hostile; we don't want a runaway
# clone to wedge the worker forever.
CLONE_TIMEOUT_SECONDS = 120


class CloneError(Exception):
    """Raised when a clone fails for any reason - timeout, auth, network, etc."""
    pass


def clone_repo(scan_id: str, repo_url: str) -> Path:
    """
    Clone repo_url into /workspace/<scan_id>/ and return the path.

    Raises CloneError on any failure with a human-readable message.
    """
    target_dir = WORKSPACE_ROOT / scan_id

    # Safety: if a previous run left files here, wipe them. Scans should
    # always start from a clean slate.
    if target_dir.exists():
        logger.info("Removing stale workspace at %s", target_dir)
        shutil.rmtree(target_dir)

    target_dir.parent.mkdir(parents=True, exist_ok=True)

    # --depth 1 = shallow clone, only the latest commit. Way faster than
    # cloning full history, and we don't care about commit graphs for scanning.
    # --single-branch keeps us from pulling all branches.
    cmd = [
        "git", "clone",
        "--depth", "1",
        "--single-branch",
        repo_url,
        str(target_dir),
    ]

    logger.info("Cloning %s into %s", repo_url, target_dir)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=CLONE_TIMEOUT_SECONDS,
            check=False,  # We inspect returncode ourselves so we can include stderr in errors
        )
    except subprocess.TimeoutExpired:
        # Timeout left a partial clone - clean it up
        if target_dir.exists():
            shutil.rmtree(target_dir, ignore_errors=True)
        raise CloneError(f"Clone timed out after {CLONE_TIMEOUT_SECONDS}s")

    if result.returncode != 0:
        # Git wrote useful diagnostics to stderr. Pass them along so the
        # API consumer knows what went wrong (bad URL, repo doesn't exist, etc.)
        stderr = result.stderr.strip() or "git clone failed with no output"
        raise CloneError(f"git clone exited {result.returncode}: {stderr}")

    logger.info("Clone successful: %s", target_dir)
    return target_dir