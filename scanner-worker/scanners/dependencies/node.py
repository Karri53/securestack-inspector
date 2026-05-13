# scanner-worker/scanners/dependencies/node.py
"""
Parser for package.json files.

package.json is JSON, so this is way simpler than requirements.txt - no
regex acrobatics needed. We extract every key from the four standard
dependency sections: dependencies, devDependencies, peerDependencies,
optionalDependencies.

We don't currently distinguish between dev and prod deps in the finding,
but the manifest section is recorded in extra_data so later analysis can
filter (e.g., "show me high-severity vulns in PROD deps only").
"""
import json
import logging
from pathlib import Path
from typing import List

from .base import ParsedPackage

logger = logging.getLogger(__name__)

# All the sections npm understands. peerDependencies are deps the consumer
# is expected to provide; optionalDependencies don't fail if missing.
# We track all of them - they're all real surface area for vulnerabilities.
DEPENDENCY_KEYS = (
    "dependencies",
    "devDependencies",
    "peerDependencies",
    "optionalDependencies",
)


def parse_package_json(file_path: Path, repo_root: Path) -> List[ParsedPackage]:
    """Parse a package.json and return one ParsedPackage per dependency entry."""
    results: List[ParsedPackage] = []
    relative_path = str(file_path.relative_to(repo_root))

    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
        data = json.loads(text)
    except (OSError, json.JSONDecodeError) as e:
        # Malformed package.json is a real-world thing. Log and move on
        # rather than failing the whole scan.
        logger.warning("Could not parse %s: %s", file_path, e)
        return results

    if not isinstance(data, dict):
        logger.warning("%s is not a JSON object at the root", relative_path)
        return results

    for section in DEPENDENCY_KEYS:
        deps = data.get(section)
        if not isinstance(deps, dict):
            continue
        for name, version_spec in deps.items():
            if not isinstance(name, str):
                continue
            results.append(ParsedPackage(
                name=name,
                version=str(version_spec) if version_spec is not None else None,
                ecosystem="npm",
                manifest_path=relative_path,
            ))

    logger.info("Parsed %d packages from %s", len(results), relative_path)
    return results