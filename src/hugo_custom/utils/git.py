from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
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


def git_last_commit(site: SiteConfig, path: Path) -> dict | None:
    """Info about the last commit touching `path`, or None when the file is
    not tracked by git."""
    cmd = [
        "git",
        "log",
        "-1",
        "--format=%H%x09%an%x09%aI",
        "--",
        str(path),
    ]
    try:
        out = subprocess.run(
            cmd, cwd=site.root, capture_output=True, text=True, check=False
        ).stdout.strip()
    except OSError:
        return None
    if not out:
        return None
    full_hash, author, date = out.split("\t")
    return {"hash": full_hash[:8], "author": author, "date": date}


def last_commit_info(site: SiteConfig, path: Path) -> dict | None:
    """Git info for the last commit touching `path`; falls back to the file's
    filesystem modification time when there is no git history."""
    info = git_last_commit(site, path)
    if info:
        return info
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
    except OSError:
        return None
    return {"date": mtime.astimezone().isoformat()}


def apply_git_meta(site: SiteConfig, src: Path, meta: dict) -> None:
    info = last_commit_info(site, src)
    if info:
        meta["lastmod"] = info["date"][:10]
        if info.get("hash"):
            meta["lastcommit"] = info["hash"]
            meta["lastcommit_author"] = info["author"]
            meta["lastcommit_date"] = info["date"]
