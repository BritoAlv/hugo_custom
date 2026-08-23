from __future__ import annotations

"""Backwards-compatibility shim: re-exports from plugins.assets.vendors."""

from hugo_custom.plugins.assets.vendors import (  # noqa: F401
    ensure_echarts,
    ensure_file_icons,
    ensure_fonts,
    ensure_katex,
    ensure_mermaid,
)
