from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hugo_custom.config import SiteConfig


def rel_of(site: SiteConfig, path: Path) -> str:
    return path.relative_to(site.source).as_posix()


def url_rel(rel: str) -> str:
    """Strip leading dots from path segments so Hugo renders them (hidden
    files and directories are skipped by Hugo)."""
    return "/".join(seg.lstrip(".") for seg in rel.split("/"))
