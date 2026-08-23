from __future__ import annotations

from abc import ABC
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hugo_custom.builder.context import StageContext


class Plugin(ABC):
    name: str

    def handles(self, src: Path) -> bool:
        return False

    def process(self, ctx: StageContext, src: Path) -> None:
        pass

    def post_stage(self, ctx: StageContext) -> None:
        pass
