from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from hugo_custom.plugins.base import Plugin

if TYPE_CHECKING:
    from hugo_custom.builder.context import StageContext


class RawPlugin(Plugin):
    name = "raw"

    def handles(self, src: Path) -> bool:
        return True

    def process(self, ctx: StageContext, src: Path) -> None:
        ctx.copy_static(src)
        ctx.record_node(ctx.rel_of(src), src.name, "file")
