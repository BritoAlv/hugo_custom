from __future__ import annotations

from typing import TYPE_CHECKING

import yaml

from hugo_custom.utils.assets.constants import CODE_EXTENSIONS, DEFAULT_ICON, EXT_ICONS
from hugo_custom.utils.fs import write_if_changed
from hugo_custom.utils.paths import rel_of, url_rel
from hugo_custom.utils.text import humanize

from .constants import PREVIEW_KINDS

if TYPE_CHECKING:
    from .builder import Builder


def tree(builder: Builder) -> dict:
    site = builder.site
    tree: dict = {"dirs": {}, "files": []}

    def add(parts: list[str], kind: str, href: str, icon: str | None) -> None:
        node = tree
        for part in parts[:-1]:
            node = node["dirs"].setdefault(part, {"dirs": {}, "files": []})
        node["files"].append((kind, parts[-1], href, icon))

    for p in sorted(builder.published, key=lambda x: rel_of(site, x).lower()):
        rel = url_rel(rel_of(site, p))
        ext = p.suffix.lower()
        parts = rel.split("/")
        if ext == ".md":
            add(parts, "md", "/" + rel[: -len(".md")] + "/", EXT_ICONS[".md"])
        elif ext == ".ipynb":
            add(parts, "nb", "/" + rel + "/", EXT_ICONS[".ipynb"])
        elif ext in CODE_EXTENSIONS:
            from hugo_custom.utils.assets.constants import LOCK_ICONS

            icon = LOCK_ICONS.get(p.name) or EXT_ICONS.get(ext, DEFAULT_ICON)
            from .constants import CODE_OUTPUT_DIR

            add(parts, "code", f"/{CODE_OUTPUT_DIR}/{rel}/", icon)
        else:
            if ext in PREVIEW_KINDS:
                from .constants import PREVIEW_OUTPUT_DIR

                add(
                    parts,
                    "file",
                    f"/{PREVIEW_OUTPUT_DIR}/{rel}/",
                    EXT_ICONS.get(ext) or DEFAULT_ICON,
                )
            else:
                add(parts, "file", "/" + rel, EXT_ICONS.get(ext) or DEFAULT_ICON)
    return tree


def sidebar_entries(builder: Builder) -> list[dict]:
    t = tree(builder)
    out: list[dict] = [{"href": "/", "text": builder.site.title}]

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

    for name, node in sorted(t["dirs"].items(), key=lambda kv: kv[0].lower()):
        item = section(humanize(name), node)
        if item is not None:
            out.append(item)
    page_files = sorted(t["files"], key=lambda f: f[1].lower())
    for kind, name, href, icon in page_files:
        out.append(file_entry(kind, name, href, icon))
    out.append({"href": "/tags/", "text": "Tags"})
    if builder.site.params.get("graph", True):
        out.append({"href": "/graph/", "text": "Graph"})
    return out


def stage_sidebar(builder: Builder) -> None:
    data = {"entries": sidebar_entries(builder)}
    write_if_changed(
        builder.site.stage / "data" / "sidebar.yml",
        yaml.safe_dump(
            data, sort_keys=False, allow_unicode=True, default_flow_style=False
        ),
    )
