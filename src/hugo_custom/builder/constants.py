from __future__ import annotations

from hugo_custom.utils.constants import CODE_OUTPUT_DIR, GRAPH_PAGE, PREVIEW_KINDS, PREVIEW_OUTPUT_DIR
from hugo_custom.utils.paths import package_dir, templates_dir

PACKAGE_DIR = package_dir()
TEMPLATES = templates_dir()

# Legacy: CSS_MODULES moved to plugins.assets.constants; keep shim for compatibility.
try:
    from hugo_custom.plugins.assets.constants import CSS_MODULES
except ImportError:
    CSS_MODULES: list[str] = [
        "tokens",
        "base",
        "header",
        "search",
        "layout",
        "sidebar",
        "nav-drawer",
        "toc",
        "content",
        "graph",
    ]

__all__ = [
    "CODE_OUTPUT_DIR",
    "CSS_MODULES",
    "GRAPH_PAGE",
    "PACKAGE_DIR",
    "PREVIEW_KINDS",
    "PREVIEW_OUTPUT_DIR",
    "TEMPLATES",
]
