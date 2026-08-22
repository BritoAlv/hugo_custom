from __future__ import annotations

from pathlib import Path


def write_if_changed(dst: Path, content: str) -> None:
    if dst.is_file() and dst.read_text(encoding="utf-8") == content:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(content, encoding="utf-8")
