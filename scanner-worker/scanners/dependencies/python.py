# scanner-worker/scanners/dependencies/python.py
"""
Parser for Python requirements.txt files.

Real-world requirements.txt is messy. We handle the common cases and skip
the weird ones (editable installs, hash-pinning, includes). Worth knowing
what we deliberately don't handle so nothing surprises us later:

  - `-e git+https://...`      (editable installs - need to parse the git URL)
  - `--hash=sha256:...`        (hash pinning - extra metadata we don't use yet)
  - `-r other-file.txt`        (file includes - would need recursive parsing)
  - `--index-url ...`          (alternate index - not a dep)
  - `--extra-index-url ...`    (same)

These are all SKIPPED, not errors. We just collect the regular `package==version`
lines and move on. A "thorough" Phase 3 parser would handle these too;
"good enough for inventory" is the right bar here.
"""
import logging
import re
from pathlib import Path
from typing import List

from .base import ParsedPackage

logger = logging.getLogger(__name__)

# Lines we explicitly skip. Order matters: check these BEFORE trying to parse.
SKIP_PREFIXES = ("-e", "-r", "-c", "--", "#")

# Strips inline comments: "package==1.0 # production only" -> "package==1.0"
INLINE_COMMENT_RE = re.compile(r"\s+#.*$")

# Splits a requirement spec into name and version. Captures:
#   - name: any chars that aren't a version operator
#   - version_spec: everything from the first operator onward (==, >=, <=, ~=, !=, <, >, ===)
# Examples:
#   "requests"                  -> name="requests", version=None
#   "requests==2.28.0"          -> name="requests", version="==2.28.0"
#   "requests>=2.0,<3.0"        -> name="requests", version=">=2.0,<3.0"
#   "package[extra]==1.0"       -> name="package[extra]", version="==1.0"
REQ_RE = re.compile(
    r"^(?P<name>[A-Za-z0-9_.\-]+(?:\[[A-Za-z0-9_,\-]+\])?)"
    r"(?P<version>([<>=!~]=?|===).*)?$"
)


def parse_requirements_txt(file_path: Path, repo_root: Path) -> List[ParsedPackage]:
    """
    Parse a requirements.txt file and return one ParsedPackage per dependency.

    Never raises on malformed input - logs and skips. A scan partially failing
    because one weird line confused the parser is worse than just missing that line.
    """
    results: List[ParsedPackage] = []
    relative_path = str(file_path.relative_to(repo_root))

    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        logger.warning("Could not read %s: %s", file_path, e)
        return results

    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        # Strip inline comments first, then whitespace
        line = INLINE_COMMENT_RE.sub("", raw_line).strip()

        if not line:
            continue
        if line.startswith(SKIP_PREFIXES):
            continue

        match = REQ_RE.match(line)
        if not match:
            logger.debug("Skipping unparseable line %d in %s: %r", line_no, relative_path, raw_line)
            continue

        name = match.group("name")
        version_spec = match.group("version") or None

        results.append(ParsedPackage(
            name=name,
            version=version_spec,
            ecosystem="pypi",
            manifest_path=relative_path,
        ))

    logger.info("Parsed %d packages from %s", len(results), relative_path)
    return results