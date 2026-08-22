from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from hugo_custom.utils.assets.constants import LANGS
from hugo_custom.utils.fs import write_if_changed
from hugo_custom.utils.git import git_date, last_commit_info
from hugo_custom.utils.links import rebase_links
from hugo_custom.utils.markdown import (
    csv_to_markdown,
    extract_tags,
    front_matter,
    ipynb_to_markdown,
    split_front_matter,
    split_title,
)
from hugo_custom.utils.paths import rel_of, url_rel
from hugo_custom.utils.text import humanize, slugify

from .constants import CODE_OUTPUT_DIR, PREVIEW_KINDS, PREVIEW_OUTPUT_DIR

if TYPE_CHECKING:
    from .builder import Builder


def apply_git_meta(builder: Builder, src: Path, meta: dict) -> None:
    info = last_commit_info(builder.site, src)
    if info:
        meta["lastmod"] = info["date"][:10]
        if info.get("hash"):
            meta["lastcommit"] = info["hash"]
            meta["lastcommit_author"] = info["author"]
            meta["lastcommit_date"] = info["date"]


def write_page(builder: Builder, src: Path) -> None:
    site = builder.site
    rel = rel_of(site, src)
    text = src.read_text(encoding="utf-8")
    meta: dict | None
    meta, body = split_front_matter(text)
    if meta is None:
        meta = {}
    created = git_date(site, src, first=True)
    apply_git_meta(builder, src, meta)
    if created is None and meta.get("lastmod"):
        created = meta["lastmod"]
    if created:
        meta.setdefault("date", created)
    tags = meta.get("categories") or meta.get("keywords") or meta.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    tags = [str(t) for t in tags]
    for tag in extract_tags(body):
        if tag not in tags:
            tags.append(tag)
    meta.pop("categories", None)
    meta.pop("keywords", None)
    if tags:
        meta["tags"] = tags
    parts = rel.split("/")
    if len(parts) > 1:
        meta.setdefault("image", f"{site.site_url}og/{slugify(parts[0])}.png")
    if "title" not in meta:
        title, body = split_title(body)
        if title:
            meta["title"] = title
    builder.pages.append((rel, tags, created or ""))
    builder.register_node(rel, meta.get("title") or src.stem)
    builder.add_refs(rel, body)
    write_if_changed(
        site.stage / "content" / url_rel(rel), front_matter(meta) + body
    )


def write_notebook(builder: Builder, src: Path) -> None:
    site = builder.site
    rel = rel_of(site, src)
    nb = json.loads(src.read_text(encoding="utf-8"))
    nb_meta = nb.get("metadata") or {}
    meta: dict = {}
    if nb_meta.get("title"):
        meta["title"] = str(nb_meta["title"])
    else:
        meta["title"] = humanize(src.stem)
    created = git_date(site, src, first=True)
    apply_git_meta(builder, src, meta)
    if created is None and meta.get("lastmod"):
        created = meta["lastmod"]
    if created:
        meta["date"] = created
    tags = nb_meta.get("categories") or nb_meta.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    tags = [str(t) for t in tags]
    if tags:
        meta["tags"] = tags
    parts = rel.split("/")
    if len(parts) > 1:
        meta["image"] = f"{site.site_url}og/{slugify(parts[0])}.png"
    builder.pages.append((rel, tags, created or ""))
    body = ipynb_to_markdown(nb)
    builder.register_node(rel, meta.get("title") or src.stem)
    builder.add_refs(rel, body)
    write_if_changed(
        site.stage / "content" / f"{url_rel(rel)}.md", front_matter(meta) + body
    )


def write_codeview(builder: Builder, src: Path) -> None:
    site = builder.site
    rel = url_rel(rel_of(site, src))
    try:
        src.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return
    lang = LANGS.get(src.suffix.lower(), "text")
    if src.name in ("Cargo.lock", "uv.lock") and src.suffix.lower() == ".lock":
        lang = "toml"
    page_dir = os.path.join(CODE_OUTPUT_DIR, str(Path(rel).parent), Path(rel).name)
    download = os.path.relpath(rel, page_dir)
    meta = {"title": src.name, "rel": rel, "lang": lang, "download": download}
    apply_git_meta(builder, src, meta)
    write_if_changed(
        site.stage / "content" / CODE_OUTPUT_DIR / f"{rel}.md",
        front_matter(meta),
    )
    builder.pages.append((f"{CODE_OUTPUT_DIR}/{rel}", [], ""))
    builder.register_node(rel_of(site, src), src.name)


def write_preview(builder: Builder, src: Path) -> None:
    site = builder.site
    rel = url_rel(rel_of(site, src))
    kind = PREVIEW_KINDS[src.suffix.lower()]
    page_dir = os.path.join(
        PREVIEW_OUTPUT_DIR, str(Path(rel).parent), Path(rel).name
    )
    download = os.path.relpath(rel, page_dir)
    meta = {
        "title": src.name,
        "rel": rel,
        "kind": kind,
        "download": download,
    }
    apply_git_meta(builder, src, meta)
    body = ""
    if kind in ("csv", "text"):
        try:
            text = src.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = ""
        body = csv_to_markdown(text) if kind == "csv" else f"```text\n{text}\n```"
    write_if_changed(
        site.stage / "content" / PREVIEW_OUTPUT_DIR / f"{rel}.md",
        front_matter(meta) + body,
    )
    builder.pages.append((f"{PREVIEW_OUTPUT_DIR}/{rel}", [], ""))
    builder.register_node(rel_of(site, src), src.name)


def stage_homepage(builder: Builder) -> bool:
    site = builder.site
    if not site.homepage:
        return False
    rel = site.homepage
    src = site.source / rel
    if not src.is_file() or src.suffix.lower() != ".md":
        print(
            f"warning: homepage file {rel!r} not found in source (must be a .md file)",
            file=sys.stderr,
        )
        return False
    if rel not in builder.published_rels:
        print(
            f"warning: homepage file {rel!r} is not published in this build",
            file=sys.stderr,
        )
        return False
    text = src.read_text(encoding="utf-8")
    meta, body = split_front_matter(text)
    if meta is None:
        meta = {}
    meta.setdefault("title", site.title)
    meta.pop("rel", None)
    if builder.site.params.get("graph", True):
        builder.nodes.setdefault(
            "/", {"label": meta.get("title") or site.title, "kind": "md"}
        )
        builder.add_refs(rel, body, source="/")
    body = rebase_links(body, str(Path(rel).parent))
    apply_git_meta(builder, src, meta)
    write_if_changed(
        site.stage / "content" / "_index.md", front_matter(meta) + body
    )
    return True


def copy_raw(builder: Builder, src: Path) -> None:
    site = builder.site
    dst = site.stage / "static" / url_rel(rel_of(site, src))
    if (
        not dst.exists()
        or dst.stat().st_size != src.stat().st_size
        or dst.stat().st_mtime_ns != src.stat().st_mtime_ns
    ):
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def clean_content(builder: Builder, expected: set[str]) -> None:
    content = builder.site.stage / "content"
    if not content.is_dir():
        return
    for dirpath, _dirnames, filenames in os.walk(content):
        rel_dir = Path(dirpath).relative_to(content).as_posix()
        for f in filenames:
            key = f if rel_dir == "." else f"{rel_dir}/{f}"
            if key not in expected:
                (Path(dirpath) / f).unlink()


def clean_static(builder: Builder, expected: set[str]) -> None:
    static = builder.site.stage / "static"
    if not static.is_dir():
        return
    protected = {"og", "icons", "vendor", "css", "js"}
    for dirpath, dirnames, filenames in os.walk(static):
        dirnames[:] = [d for d in dirnames if d not in protected]
        rel_dir = Path(dirpath).relative_to(static).as_posix()
        for f in filenames:
            key = f if rel_dir == "." else f"{rel_dir}/{f}"
            if key not in expected:
                (Path(dirpath) / f).unlink()
    for dirpath, dirnames, filenames in os.walk(static, topdown=False):
        for d in dirnames:
            if d in protected:
                continue
            p = Path(dirpath) / d
            if p.is_dir() and not any(p.iterdir()):
                p.rmdir()
