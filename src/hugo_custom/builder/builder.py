from __future__ import annotations

from pathlib import Path

from hugo_custom.config import SiteConfig
from hugo_custom.files import collect, load_specs
from hugo_custom.utils.assets.constants import CODE_EXTENSIONS
from hugo_custom.utils.paths import rel_of, url_rel

from .constants import CODE_OUTPUT_DIR, GRAPH_PAGE, PREVIEW_KINDS, PREVIEW_OUTPUT_DIR


class Builder:
    def __init__(self, site: SiteConfig, deploy: bool, preview_mode: bool = False):
        self.site = site
        self.deploy = deploy
        self.preview_mode = preview_mode
        self.specs = load_specs(site, deploy)
        self.published = collect(site, self.specs)
        self.published_rels = {rel_of(site, p) for p in self.published}
        self.pages: list[tuple[str, list[str], str]] = []
        self.nodes: dict[str, dict] = {}
        self.links: dict[str, set[str]] = {}

    # ---------- staging ----------
    def stage(self) -> None:

        stage, site = self.site.stage, self.site
        stage.mkdir(parents=True, exist_ok=True)
        (stage / "content").mkdir(parents=True, exist_ok=True)
        (stage / "static").mkdir(parents=True, exist_ok=True)
        content_expected: set[str] = set()
        static_expected: set[str] = set()
        for src in self.published:
            rel = rel_of(site, src)
            urel = url_rel(rel)
            ext = src.suffix.lower()
            if ext == ".md":
                content_expected.add(urel)
                self.write_page(src)
            elif ext == ".ipynb":
                content_expected.add(f"{urel}.md")
                self.write_notebook(src)
            elif ext in CODE_EXTENSIONS:
                content_expected.add(f"{CODE_OUTPUT_DIR}/{urel}.md")
                static_expected.add(urel)
                self.copy_raw(src)
                self.write_codeview(src)
            else:
                static_expected.add(urel)
                self.copy_raw(src)
                self.register_node(rel, src.name)
                if src.suffix.lower() in PREVIEW_KINDS:
                    content_expected.add(f"{PREVIEW_OUTPUT_DIR}/{urel}.md")
                    self.write_preview(src)
        home_staged = self.stage_homepage()
        if home_staged:
            content_expected.add("_index.md")
        if self.site.params.get("graph", True):
            content_expected.add(GRAPH_PAGE)
        self.clean_content(content_expected)
        self.clean_static(static_expected)
        self.stage_assets()
        self.stage_sidebar()
        self.stage_graph()
        self.stage_config()

    def stage_homepage(self) -> bool:
        from .staging import stage_homepage as _fn

        return _fn(self)

    def apply_git_meta(self, src: Path, meta: dict) -> None:
        from .staging import apply_git_meta as _fn

        return _fn(self, src, meta)

    def write_page(self, src: Path) -> None:
        from .staging import write_page as _fn

        return _fn(self, src)

    def write_notebook(self, src: Path) -> None:
        from .staging import write_notebook as _fn

        return _fn(self, src)

    def write_codeview(self, src: Path) -> None:
        from .staging import write_codeview as _fn

        return _fn(self, src)

    def write_preview(self, src: Path) -> None:
        from .staging import write_preview as _fn

        return _fn(self, src)

    def copy_raw(self, src: Path) -> None:
        from .staging import copy_raw as _fn

        return _fn(self, src)

    def clean_content(self, expected: set[str]) -> None:
        from .staging import clean_content as _fn

        return _fn(self, expected)

    def clean_static(self, expected: set[str]) -> None:
        from .staging import clean_static as _fn

        return _fn(self, expected)

    # ---------- reference graph ----------
    def page_url(self, rel: str) -> str | None:
        from .graph import page_url as _fn

        return _fn(self, rel)

    def node_kind(self, rel: str) -> str:
        from .graph import node_kind as _fn

        return _fn(self, rel)

    def register_node(self, rel: str, label: str) -> None:
        from .graph import register_node as _fn

        return _fn(self, rel, label)

    def add_refs(self, rel: str, body: str, source: str | None = None) -> None:
        from .graph import add_refs as _fn

        return _fn(self, rel, body, source)

    def graph_payload(self) -> dict:
        from .graph import graph_payload as _fn

        return _fn(self)

    def stage_graph(self) -> None:
        from .graph import stage_graph as _fn

        return _fn(self)

    # ---------- tree / sidebar ----------
    def tree(self) -> dict:
        from .sidebar import tree as _fn

        return _fn(self)

    def sidebar_entries(self) -> list[dict]:
        from .sidebar import sidebar_entries as _fn

        return _fn(self)

    def stage_sidebar(self) -> None:
        from .sidebar import stage_sidebar as _fn

        return _fn(self)

    # ---------- assets ----------
    def icon_for(self, src: Path) -> str | None:
        from .assets_stage import icon_for as _fn

        return _fn(self, src)

    def stage_assets(self) -> None:
        from .assets_stage import stage_assets as _fn

        return _fn(self)

    def css_bundle(self) -> str:
        from .assets_stage import css_bundle as _fn

        return _fn(self)

    def tsc_cmd(self) -> list[str] | None:
        from .assets_stage import tsc_cmd as _fn

        return _fn(self)

    def stage_js(self) -> None:
        from .assets_stage import stage_js as _fn

        return _fn(self)

    def stage_config(self) -> None:
        from .assets_stage import stage_config as _fn

        return _fn(self)

    # ---------- rendering ----------
    def render(self) -> None:
        from .render import render as _fn

        return _fn(self)

    def preview(self, host: str = "127.0.0.1") -> None:
        from .render import preview as _fn

        return _fn(self, host)

    def summary(self) -> None:
        from .render import summary as _fn

        return _fn(self)
