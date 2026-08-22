from __future__ import annotations

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parents[1]
TEMPLATES = PACKAGE_DIR / "templates"

CODE_OUTPUT_DIR = "codeview"
PREVIEW_OUTPUT_DIR = "preview"
GRAPH_PAGE = "graph.md"

PREVIEW_KINDS: dict[str, str] = {
    ".svg": "svg",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".gif": "image",
    ".webp": "image",
    ".ico": "image",
    ".bmp": "image",
    ".mp4": "video",
    ".webm": "video",
    ".mov": "video",
    ".mkv": "video",
    ".avi": "video",
    ".ogv": "video",
    ".mp3": "audio",
    ".wav": "audio",
    ".ogg": "audio",
    ".flac": "audio",
    ".m4a": "audio",
    ".pdf": "pdf",
    ".csv": "csv",
    ".xml": "text",
    ".txt": "text",
    ".ini": "text",
    ".cfg": "text",
}

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
