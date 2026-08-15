from __future__ import annotations

import os
from pathlib import Path

import pathspec

from hugo_custom.config import SiteConfig


def load_specs(
    site: SiteConfig, deploy: bool
) -> list[tuple[str, pathspec.GitIgnoreSpec]]:
    specs: list[tuple[str, pathspec.GitIgnoreSpec]] = []

    def add(path: Path, base: str) -> None:
        if not path.is_file():
            return
        lines = path.read_text(encoding="utf-8").splitlines()
        if lines:
            specs.append((base, pathspec.GitIgnoreSpec.from_lines(lines)))

    add(site.root / ".gitignore", "")
    for ignore in site.source.rglob(".gitignore"):
        base = ignore.parent.relative_to(site.root).as_posix()
        add(ignore, base)
    if deploy and site.siteignore is not None:
        add(site.siteignore, "")
    if site.ignore:
        specs.append(("", pathspec.GitIgnoreSpec.from_lines(site.ignore)))
    return specs


def is_ignored(
    rel_from_root: str, specs: list[tuple[str, pathspec.GitIgnoreSpec]]
) -> bool:
    for base, spec in specs:
        if base:
            if rel_from_root != base and not rel_from_root.startswith(f"{base}/"):
                continue
            local = rel_from_root[len(base) :].lstrip("/")
        else:
            local = rel_from_root
        if spec.match_file(local):
            return True
    return False


def collect(
    site: SiteConfig, specs: list[tuple[str, pathspec.GitIgnoreSpec]]
) -> list[Path]:
    published: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(site.source):
        kept_dirs = []
        for d in dirnames:
            if d == ".git":
                continue
            rel_root = (Path(dirpath) / d).relative_to(site.root).as_posix()
            if not is_ignored(rel_root, specs):
                kept_dirs.append(d)
        dirnames[:] = kept_dirs
        for f in filenames:
            if f in (".gitignore", ".siteignore", "__init__.py"):
                continue
            rel_root = (Path(dirpath) / f).relative_to(site.root).as_posix()
            if not is_ignored(rel_root, specs):
                published.append(Path(dirpath) / f)
    return published


def rel_of(site: SiteConfig, path: Path) -> str:
    return path.relative_to(site.source).as_posix()


def url_rel(rel: str) -> str:
    """Strip leading dots from path segments so Hugo renders them (hidden
    files and directories are skipped by Hugo)."""
    return "/".join(seg.lstrip(".") for seg in rel.split("/"))
