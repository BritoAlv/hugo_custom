from __future__ import annotations

import subprocess
from pathlib import Path

from hugo_custom.config import SiteConfig


def git_date(site: SiteConfig, path: Path, first: bool) -> str | None:
    if first:
        cmd = ["git", "log", "--diff-filter=A", "--format=%aI", "--", str(path)]
    else:
        cmd = ["git", "log", "-1", "--format=%aI", "--", str(path)]
    try:
        out = subprocess.run(
            cmd, cwd=site.root, capture_output=True, text=True, check=False
        ).stdout.strip()
    except OSError:
        return None
    return out[:10] if out else None
