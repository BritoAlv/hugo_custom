from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from hugo_custom.config import SiteConfig
from hugo_custom.utils.fs import write_if_changed
from hugo_custom.utils.paths import rel_of, url_rel


@dataclass
class NodeEntry:
    rel: str
    label: str
    kind: str
    body: str = ""
    source: str | None = None


@dataclass
class StageContext:
    site: SiteConfig
    published: list[Path]
    published_rels: set[str]
    pages: list[tuple[str, list[str], str]] = field(default_factory=list)
    node_registry: list[NodeEntry] = field(default_factory=list)
    content_expected: set[str] = field(default_factory=set)
    static_expected: set[str] = field(default_factory=set)

    def rel_of(self, src: Path) -> str:
        return rel_of(self.site, src)

    def url_rel(self, rel: str) -> str:
        return url_rel(rel)

    def write_content(self, rel: str, text: str) -> None:
        write_if_changed(self.site.stage / "content" / rel, text)
        self.content_expected.add(rel)

    def write_static(self, rel: str, text: str) -> None:
        write_if_changed(self.site.stage / "static" / rel, text)
        self.static_expected.add(rel)

    def copy_static(self, src: Path) -> None:
        dst = self.site.stage / "static" / url_rel(rel_of(self.site, src))
        if (
            not dst.exists()
            or dst.stat().st_size != src.stat().st_size
            or dst.stat().st_mtime_ns != src.stat().st_mtime_ns
        ):
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        self.static_expected.add(url_rel(rel_of(self.site, src)))

    def record_node(
        self,
        rel: str,
        label: str,
        kind: str,
        body: str = "",
        source: str | None = None,
    ) -> None:
        self.node_registry.append(NodeEntry(rel=rel, label=label, kind=kind, body=body, source=source))
