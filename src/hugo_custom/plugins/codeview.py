from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from hugo_custom.plugins.base import Plugin
from hugo_custom.utils.constants import CODE_OUTPUT_DIR
from hugo_custom.utils.extensions import LANGS
from hugo_custom.utils.git import apply_git_meta
from hugo_custom.utils.markdown import front_matter

if TYPE_CHECKING:
    from hugo_custom.builder.context import StageContext


class CodeViewPlugin(Plugin):
    name = "codeview"

    def handles(self, src: Path) -> bool:
        from hugo_custom.utils.extensions import CODE_EXTENSIONS

        return src.suffix.lower() in CODE_EXTENSIONS

    def process(self, ctx: StageContext, src: Path) -> None:
        urel = ctx.url_rel(ctx.rel_of(src))
        try:
            src.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            ctx.copy_static(src)
            return
        lang = LANGS.get(src.suffix.lower(), "text")
        if src.name in ("Cargo.lock", "uv.lock") and src.suffix.lower() == ".lock":
            lang = "toml"
        page_dir = os.path.join(CODE_OUTPUT_DIR, str(Path(urel).parent), Path(urel).name)
        download = os.path.relpath(urel, page_dir)
        meta = {"title": src.name, "rel": urel, "lang": lang, "download": download}
        apply_git_meta(ctx.site, src, meta)
        ctx.write_content(f"{CODE_OUTPUT_DIR}/{urel}.md", front_matter(meta))
        ctx.pages.append((f"{CODE_OUTPUT_DIR}/{urel}", [], ""))
        ctx.record_node(ctx.rel_of(src), src.name, "code")
        ctx.copy_static(src)
