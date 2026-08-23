from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from hugo_custom.plugins.base import Plugin
from hugo_custom.utils.constants import PREVIEW_KINDS
from hugo_custom.utils.extensions import CODE_EXTENSIONS, DEFAULT_ICON, EXT_ICONS
from hugo_custom.utils.text import humanize

if TYPE_CHECKING:
    from hugo_custom.builder.context import StageContext


class SidebarPlugin(Plugin):
    name = "sidebar"

    def post_stage(self, ctx: StageContext) -> None:
        tree = self._tree(ctx)
        entries = self._sidebar_entries(ctx, tree)
        data = {"entries": entries}
        path = ctx.site.stage / "data" / "sidebar.yml"
        path.parent.mkdir(parents=True, exist_ok=True)
        content = yaml.safe_dump(
            data, sort_keys=False, allow_unicode=True, default_flow_style=False
        )
        # sidebar data is not part of content/static cleanup; write directly
        from hugo_custom.utils.fs import write_if_changed

        write_if_changed(path, content)

    def _tree(self, ctx: StageContext) -> dict:
        tree: dict = {"dirs": {}, "files": []}

        def add(parts: list[str], kind: str, href: str, icon: str | None) -> None:
            node = tree
            for part in parts[:-1]:
                node = node["dirs"].setdefault(part, {"dirs": {}, "files": []})
            node["files"].append((kind, parts[-1], href, icon))

        for p in sorted(ctx.published, key=lambda x: ctx.rel_of(x).lower()):
            rel = ctx.url_rel(ctx.rel_of(p))
            ext = p.suffix.lower()
            parts = rel.split("/")
            if ext == ".md":
                add(parts, "md", "/" + rel[: -len(".md")] + "/", EXT_ICONS[".md"])
            elif ext == ".ipynb":
                add(parts, "nb", "/" + rel + "/", EXT_ICONS[".ipynb"])
            elif ext in CODE_EXTENSIONS:
                from hugo_custom.utils.extensions import LOCK_ICONS

                icon = LOCK_ICONS.get(p.name) or EXT_ICONS.get(ext, DEFAULT_ICON)
                from hugo_custom.utils.constants import CODE_OUTPUT_DIR

                add(parts, "code", f"/{CODE_OUTPUT_DIR}/{rel}/", icon)
            else:
                if ext in PREVIEW_KINDS:
                    from hugo_custom.utils.constants import PREVIEW_OUTPUT_DIR

                    add(
                        parts,
                        "file",
                        f"/{PREVIEW_OUTPUT_DIR}/{rel}/",
                        EXT_ICONS.get(ext) or DEFAULT_ICON,
                    )
                else:
                    add(parts, "file", "/" + rel, EXT_ICONS.get(ext) or DEFAULT_ICON)
        return tree

    def _sidebar_entries(self, ctx: StageContext, tree: dict) -> list[dict]:
        out: list[dict] = [{"href": "/", "text": ctx.site.title}]

        def file_entry(kind: str, name: str, href: str, icon: str | None) -> dict:
            entry: dict = {"href": href, "text": name, "kind": kind}
            if icon:
                entry["icon"] = icon
            return entry

        def section(label: str, node: dict) -> dict | None:
            entry: dict = {"section": label, "contents": []}
            for name, child in sorted(
                node["dirs"].items(), key=lambda kv: kv[0].lower()
            ):
                sub = section(humanize(name), child)
                if sub is not None:
                    entry["contents"].append(sub)
            page_files = sorted(node["files"], key=lambda f: f[1].lower())
            for kind, name, href, icon in page_files:
                entry["contents"].append(file_entry(kind, name, href, icon))
            return entry if entry["contents"] else None

        for name, node in sorted(tree["dirs"].items(), key=lambda kv: kv[0].lower()):
            item = section(humanize(name), node)
            if item is not None:
                out.append(item)
        page_files = sorted(tree["files"], key=lambda f: f[1].lower())
        for kind, name, href, icon in page_files:
            out.append(file_entry(kind, name, href, icon))
        out.append({"href": "/tags/", "text": "Tags"})
        if ctx.site.params.get("graph", True):
            out.append({"href": "/graph/", "text": "Graph"})
        return out
