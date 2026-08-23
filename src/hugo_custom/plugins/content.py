from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from hugo_custom.plugins.base import Plugin
from hugo_custom.utils.git import apply_git_meta, git_date
from hugo_custom.utils.markdown import (
    extract_tags,
    front_matter,
    ipynb_to_markdown,
    split_front_matter,
    split_title,
)
from hugo_custom.utils.text import humanize, slugify

if TYPE_CHECKING:
    from hugo_custom.builder.context import StageContext


class PagePlugin(Plugin):
    name = "page"

    def handles(self, src: Path) -> bool:
        return src.suffix.lower() == ".md"

    def process(self, ctx: StageContext, src: Path) -> None:
        rel = ctx.rel_of(src)
        text = src.read_text(encoding="utf-8")
        meta, body = split_front_matter(text)
        if meta is None:
            meta = {}
        created = git_date(ctx.site, src, first=True)
        apply_git_meta(ctx.site, src, meta)
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
            meta.setdefault("image", f"{ctx.site.site_url}og/{slugify(parts[0])}.png")
        if "title" not in meta:
            title, body = split_title(body)
            if title:
                meta["title"] = title
        ctx.pages.append((rel, tags, created or ""))
        ctx.record_node(rel, meta.get("title") or src.stem, "md", body)
        ctx.write_content(ctx.url_rel(rel), front_matter(meta) + body)


class NotebookPlugin(Plugin):
    name = "notebook"

    def handles(self, src: Path) -> bool:
        return src.suffix.lower() == ".ipynb"

    def process(self, ctx: StageContext, src: Path) -> None:
        rel = ctx.rel_of(src)
        nb = json.loads(src.read_text(encoding="utf-8"))
        nb_meta = nb.get("metadata") or {}
        meta: dict = {}
        if nb_meta.get("title"):
            meta["title"] = str(nb_meta["title"])
        else:
            meta["title"] = humanize(src.stem)
        created = git_date(ctx.site, src, first=True)
        apply_git_meta(ctx.site, src, meta)
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
            meta["image"] = f"{ctx.site.site_url}og/{slugify(parts[0])}.png"
        ctx.pages.append((rel, tags, created or ""))
        body = ipynb_to_markdown(nb)
        ctx.record_node(rel, meta.get("title") or src.stem, "nb", body)
        ctx.write_content(f"{ctx.url_rel(rel)}.md", front_matter(meta) + body)
