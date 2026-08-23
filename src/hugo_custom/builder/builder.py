from __future__ import annotations

import os
import shutil
from pathlib import Path

from hugo_custom.builder.context import StageContext
from hugo_custom.config import SiteConfig
from hugo_custom.files import collect, load_specs
from hugo_custom.plugins import default_plugins
from hugo_custom.plugins.base import Plugin
from hugo_custom.utils.constants import CODE_OUTPUT_DIR
from hugo_custom.utils.paths import rel_of
from hugo_custom.utils.text import slugify


def _clean_content(ctx: StageContext) -> None:
    content = ctx.site.stage / "content"
    if not content.is_dir():
        return
    for dirpath, _dirnames, filenames in os.walk(content):
        rel_dir = Path(dirpath).relative_to(content).as_posix()
        for f in filenames:
            key = f if rel_dir == "." else f"{rel_dir}/{f}"
            if key not in ctx.content_expected:
                (Path(dirpath) / f).unlink()


def _clean_static(ctx: StageContext) -> None:
    static = ctx.site.stage / "static"
    if not static.is_dir():
        return
    protected = {"og", "icons", "vendor", "css", "js"}
    for dirpath, dirnames, filenames in os.walk(static):
        dirnames[:] = [d for d in dirnames if d not in protected]
        rel_dir = Path(dirpath).relative_to(static).as_posix()
        for f in filenames:
            key = f if rel_dir == "." else f"{rel_dir}/{f}"
            if key not in ctx.static_expected:
                (Path(dirpath) / f).unlink()
    for dirpath, dirnames, filenames in os.walk(static, topdown=False):
        for d in dirnames:
            if d in protected:
                continue
            p = Path(dirpath) / d
            if p.is_dir() and not any(p.iterdir()):
                p.rmdir()


class Builder:
    def __init__(
        self, site: SiteConfig, deploy: bool, preview_mode: bool = False, plugins: list[Plugin] | None = None
    ):
        self.site = site
        self.deploy = deploy
        self.preview_mode = preview_mode
        self.specs = load_specs(site, deploy)
        self.published = collect(site, self.specs)
        self.published_rels = {rel_of(site, p) for p in self.published}
        self.plugins: list[Plugin] = plugins if plugins is not None else default_plugins()
        self.ctx = StageContext(site=site, published=self.published, published_rels=self.published_rels)
        # Backwards-compatible aliases
        self.pages = self.ctx.pages
        self.nodes: dict[str, dict] = {}
        self.links: dict[str, set[str]] = {}

    # ---------- staging ----------
    def stage(self) -> None:
        stage, site = self.site.stage, self.site
        stage.mkdir(parents=True, exist_ok=True)
        (stage / "content").mkdir(parents=True, exist_ok=True)
        (stage / "static").mkdir(parents=True, exist_ok=True)

        for src in self.published:
            for plugin in self.plugins:
                if plugin.handles(src):
                    plugin.process(self.ctx, src)
                    break

        for plugin in self.plugins:
            plugin.post_stage(self.ctx)

        _clean_content(self.ctx)
        _clean_static(self.ctx)

    # ---------- rendering ----------
    def render(self) -> None:
        from hugo_custom.utils.hugo import run_hugo

        run_hugo(self.site.stage, self.site.output, self.site.root)

    def preview(self, host: str = "127.0.0.1") -> None:
        from hugo_custom.utils.hugo import serve_hugo

        serve_hugo(self.site.stage, self.site.output, self.site.root, host)

    def summary(self) -> None:
        n_pages = len(list(self.site.output.rglob("*.html")))
        n_code = sum(1 for rel, _, _ in self.pages if rel.startswith(CODE_OUTPUT_DIR))
        n_md = sum(1 for rel, _, _ in self.pages if rel.endswith(".md"))
        n_tags = len({slugify(t) for _, tags, _ in self.pages for t in tags})
        print(f"rendered {n_pages} pages ({n_md} markdown, {n_code} code views), {n_tags} tags")
