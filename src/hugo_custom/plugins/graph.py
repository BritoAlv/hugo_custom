from __future__ import annotations

import json
import posixpath
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from hugo_custom.plugins.base import Plugin
from hugo_custom.utils.constants import CODE_OUTPUT_DIR, GRAPH_PAGE, PREVIEW_KINDS, PREVIEW_OUTPUT_DIR
from hugo_custom.utils.extensions import CODE_EXTENSIONS
from hugo_custom.utils.markdown import front_matter

if TYPE_CHECKING:
    from hugo_custom.builder.context import StageContext

FENCE_RE = re.compile(r"^\s*(```|~~~)")
LINK_RE = re.compile(r"\]\(([^)]+)\)")


def _extract_refs(body: str, base_dir: str) -> set[str]:
    refs: set[str] = set()
    out = []
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
            out.append(line)
    for line in out:
        for match in LINK_RE.finditer(line):
            dest = match.group(1).strip()
            if dest[0:1] in ("#", "/") or dest.startswith(
                ("http://", "https://", "mailto:", "data:")
            ):
                continue
            head = re.split(r"[#?]", dest, 1)[0].strip()
            if not head:
                continue
            rel = posixpath.normpath(posixpath.join(base_dir or ".", head))
            if rel in ("", ".", "..") or rel.startswith("../"):
                continue
            refs.add(rel)
    return refs


def _page_url(ctx: StageContext, rel: str) -> str | None:
    if rel not in ctx.published_rels and rel != ctx.site.homepage:
        # homepage rel is checked separately; allow it for "/"
        if rel != ctx.site.homepage:
            return None
    # for homepage we handle separately
    ext = Path(rel).suffix.lower()
    from hugo_custom.utils.paths import url_rel as _url_rel

    urel = _url_rel(rel)
    if ext == ".md":
        return "/" + urel[: -len(".md")] + "/"
    if ext == ".ipynb":
        return "/" + urel + "/"
    if ext in CODE_EXTENSIONS:
        return f"/{CODE_OUTPUT_DIR}/{urel}/"
    if ext in PREVIEW_KINDS:
        return f"/{PREVIEW_OUTPUT_DIR}/{urel}/"
    return "/" + urel


def _node_kind(rel: str) -> str:
    ext = Path(rel).suffix.lower()
    if ext == ".md":
        return "md"
    if ext == ".ipynb":
        return "nb"
    if ext in CODE_EXTENSIONS:
        return "code"
    return "file"


class GraphPlugin(Plugin):
    name = "graph"

    def post_stage(self, ctx: StageContext) -> None:
        if not ctx.site.params.get("graph", True):
            return
        nodes: dict[str, dict] = {}
        links: dict[str, set[str]] = {}

        for entry in ctx.node_registry:
            rel = entry.rel
            label = entry.label
            kind = entry.kind
            body = entry.body
            source_override = entry.source

            if source_override is not None:
                url = source_override
                nodes.setdefault(url, {"label": label, "kind": kind})
                src_url = url
            else:
                url = _page_url(ctx, rel)
                if url is None:
                    continue
                nodes.setdefault(url, {"label": label, "kind": kind or _node_kind(rel)})
                src_url = url

            if not body:
                continue

            base_dir = "" if source_override == "/" else str(Path(rel).parent)
            # for homepage, base_dir is homepage's parent
            if source_override == "/":
                base_dir = str(Path(rel).parent)

            targets: set[str] = set()
            for ref in _extract_refs(body, base_dir):
                target = _page_url(ctx, ref)
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
                if target == src_url:
                    continue
                targets.add(target)
            if targets:
                links.setdefault(src_url, set()).update(targets)

        degrees: dict[str, int] = {}
        link_list: list[dict] = []
        for source, targets in links.items():
            for target in targets:
                link_list.append({"source": source, "target": target})
                degrees[source] = degrees.get(source, 0) + 1
                degrees[target] = degrees.get(target, 0) + 1
        payload_nodes = [
            {
                "id": url,
                "label": node["label"],
                "kind": node["kind"],
                "degree": degrees.get(url, 0),
            }
            for url, node in sorted(nodes.items())
        ]
        link_list.sort(key=lambda item: (item["source"], item["target"]))
        payload = {"nodes": payload_nodes, "links": link_list}

        ctx.write_static("js/graph-data.json", json.dumps(payload, indent=2))
        ctx.write_content(GRAPH_PAGE, front_matter({"title": "Graph", "type": "graph"}))
