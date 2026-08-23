from __future__ import annotations

import csv
import io
import os
from pathlib import Path
from typing import TYPE_CHECKING

from hugo_custom.plugins.base import Plugin
from hugo_custom.utils.constants import PREVIEW_KINDS, PREVIEW_OUTPUT_DIR
from hugo_custom.utils.git import apply_git_meta
from hugo_custom.utils.markdown import front_matter

if TYPE_CHECKING:
    from hugo_custom.builder.context import StageContext


def _csv_to_markdown(text: str) -> str:
    rows = [
        row for row in csv.reader(io.StringIO(text)) if any(cell.strip() for cell in row)
    ]
    if not rows:
        return ""
    out = ["| " + " | ".join(str(c) for c in rows[0]) + " |"]
    out.append("|" + "|".join("---" for _ in rows[0]) + "|")
    for row in rows[1:]:
        out.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(out)


class PreviewPlugin(Plugin):
    name = "preview"

    def handles(self, src: Path) -> bool:
        return src.suffix.lower() in PREVIEW_KINDS

    def process(self, ctx: StageContext, src: Path) -> None:
        urel = ctx.url_rel(ctx.rel_of(src))
        kind = PREVIEW_KINDS[src.suffix.lower()]
        page_dir = os.path.join(
            PREVIEW_OUTPUT_DIR, str(Path(urel).parent), Path(urel).name
        )
        download = os.path.relpath(urel, page_dir)
        meta = {
            "title": src.name,
            "rel": urel,
            "kind": kind,
            "download": download,
        }
        apply_git_meta(ctx.site, src, meta)
        body = ""
        if kind in ("csv", "text"):
            try:
                text = src.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                text = ""
            body = _csv_to_markdown(text) if kind == "csv" else f"```text\n{text}\n```"
        ctx.write_content(f"{PREVIEW_OUTPUT_DIR}/{urel}.md", front_matter(meta) + body)
        ctx.pages.append((f"{PREVIEW_OUTPUT_DIR}/{urel}", [], ""))
        ctx.record_node(ctx.rel_of(src), src.name, "file")
        ctx.copy_static(src)
