from __future__ import annotations

from pathlib import Path

from hugo_custom.config import CONFIG_FILENAME


def find_config(start: Path) -> Path | None:
    """Locate the site configuration at the top of the repo, walking up from
    `start` (current directory) through its parents."""
    for directory in (start, *start.parents):
        candidate = directory / CONFIG_FILENAME
        if candidate.is_file():
            return candidate
    return None
