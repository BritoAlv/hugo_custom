from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from hugo_custom.plugins.base import Plugin
from hugo_custom.utils.git import apply_git_meta
from hugo_custom.utils.markdown import front_matter, split_front_matter

if TYPE_CHECKING:
    from hugo_custom.builder.context import StageContext

FENCE_RE = re.compile(r"^\s*(```|~~~)")
LINK_RE = re.compile(r"\]\(([^)]+)\)")


def _rebase_links(body: str, base_dir: str) -> str:
    if not base_dir:
        return body

    def rebase(match: re.Match) -> str:
        dest = match.group(1)
        if dest[0:1] in ("#", "/") or dest.startswith(
            ("http://", "https://", "mailto:", "data:")
        ):
            return match.group(0)
        return f"]({base_dir}/{dest})"

    out: list[str] = []
    in_fence = ""
    for line in body.splitlines(keepends=True):
        fence = FENCE_RE.match(line)
        if fence:
            marker = fence.group(1)
            if not in_fence:
                in_fence = marker
            elif line.strip().startswith(marker):
                in_fence = ""
        if not in_fence:
            line = LINK_RE.sub(rebase, line)
        out.append(line)
    return "".join(out)


class HomepagePlugin(Plugin):
    name = "homepage"

    def post_stage(self, ctx: StageContext) -> None:
        site = ctx.site
        if not site.homepage:
            return
        rel = site.homepage
        src = site.source / rel
        if not src.is_file() or src.suffix.lower() != ".md":
            print(
                f"warning: homepage file {rel!r} not found in source (must be a .md file)",
                file=sys.stderr,
            )
            return
        if rel not in ctx.published_rels:
            print(
                f"warning: homepage file {rel!r} is not published in this build",
                file=sys.stderr,
            )
            return
        text = src.read_text(encoding="utf-8")
        meta, body = split_front_matter(text)
        if meta is None:
            meta = {}
        meta.setdefault("title", site.title)
        meta.pop("rel", None)
        if site.params.get("graph", True):
            ctx.record_node(rel, meta.get("title") or site.title, "md", body, source="/")
        body = _rebase_links(body, str(Path(rel).parent))
        apply_git_meta(site, src, meta)
        ctx.write_content("_index.md", front_matter(meta) + body)
