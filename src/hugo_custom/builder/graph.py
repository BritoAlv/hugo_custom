from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from hugo_custom.utils.assets.constants import CODE_EXTENSIONS
from hugo_custom.utils.fs import write_if_changed
from hugo_custom.utils.links import extract_refs
from hugo_custom.utils.markdown import front_matter
from hugo_custom.utils.paths import url_rel

from .constants import GRAPH_PAGE, PREVIEW_KINDS

if TYPE_CHECKING:
    from .builder import Builder


def page_url(builder: Builder, rel: str) -> str | None:
    if rel not in builder.published_rels:
        return None
    ext = Path(rel).suffix.lower()
    urel = url_rel(rel)
    if ext == ".md":
        return "/" + urel[: -len(".md")] + "/"
    if ext == ".ipynb":
        return "/" + urel + "/"
    if ext in CODE_EXTENSIONS:
        from .constants import CODE_OUTPUT_DIR

        return f"/{CODE_OUTPUT_DIR}/{urel}/"
    if ext in PREVIEW_KINDS:
        from .constants import PREVIEW_OUTPUT_DIR

        return f"/{PREVIEW_OUTPUT_DIR}/{urel}/"
    return "/" + urel


def node_kind(builder: Builder, rel: str) -> str:
    _ = builder
    ext = Path(rel).suffix.lower()
    if ext == ".md":
        return "md"
    if ext == ".ipynb":
        return "nb"
    if ext in CODE_EXTENSIONS:
        return "code"
    return "file"


def register_node(builder: Builder, rel: str, label: str) -> None:
    url = page_url(builder, rel)
    if url is None:
        return
    builder.nodes.setdefault(url, {"label": label, "kind": node_kind(builder, rel)})


def add_refs(
    builder: Builder, rel: str, body: str, source: str | None = None
) -> None:
    if source is None:
        source = page_url(builder, rel)
    if source is None:
        return
    targets: set[str] = set()
    for ref in extract_refs(body, str(Path(rel).parent)):
        target = page_url(builder, ref)
        if target is None:
            if Path(ref).suffix.lower() in (
                ".md",
                ".ipynb",
                *CODE_EXTENSIONS,
                *PREVIEW_KINDS,
            ):
                print(
                    f"warning: unresolved reference from {rel!r} to {ref!r} "
                    "(not published in this build)",
                    file=sys.stderr,
                )
            continue
        if target == source:
            continue
        targets.add(target)
    if targets:
        builder.links.setdefault(source, set()).update(targets)


def graph_payload(builder: Builder) -> dict:
    degrees: dict[str, int] = {}
    links: list[dict] = []
    for source, targets in builder.links.items():
        for target in targets:
            links.append({"source": source, "target": target})
            degrees[source] = degrees.get(source, 0) + 1
            degrees[target] = degrees.get(target, 0) + 1
    nodes = [
        {
            "id": url,
            "label": node["label"],
            "kind": node["kind"],
            "degree": degrees.get(url, 0),
        }
        for url, node in sorted(builder.nodes.items())
    ]
    links.sort(key=lambda l: (l["source"], l["target"]))
    return {"nodes": nodes, "links": links}


def stage_graph(builder: Builder) -> None:
    if not builder.site.params.get("graph", True):
        return
    write_if_changed(
        builder.site.stage / "static" / "js" / "graph-data.json",
        json.dumps(graph_payload(builder), indent=2),
    )
    write_if_changed(
        builder.site.stage / "content" / GRAPH_PAGE,
        front_matter({"title": "Graph", "type": "graph"}),
    )
