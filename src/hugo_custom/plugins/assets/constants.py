from __future__ import annotations

import re

KATEX_VERSION = "0.18.4"
KATEX_TARBALL = f"https://registry.npmjs.org/katex/-/katex-{KATEX_VERSION}.tgz"

MERMAID_VERSION = "11.17.0"
MERMAID_URLS = [
    f"https://cdn.jsdelivr.net/npm/mermaid@{MERMAID_VERSION}/dist/mermaid.min.js",
    f"https://unpkg.com/mermaid@{MERMAID_VERSION}/dist/mermaid.min.js",
]

ECHARTS_VERSION = "5.6.0"
ECHARTS_URLS = [
    f"https://cdn.jsdelivr.net/npm/echarts@{ECHARTS_VERSION}/dist/echarts.min.js",
    f"https://unpkg.com/echarts@{ECHARTS_VERSION}/dist/echarts.min.js",
]

ICON_BASE = "https://cdn.jsdelivr.net/gh/vscode-icons/vscode-icons@master/icons/"

ICON_ALT_BASE = "https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/main/icons/"

ICON_ALT = {
    "file_type_csv": ICON_ALT_BASE + "table.svg",
}

GOOGLE_FONTS_URL = (
    "https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,400;0,700;1,400"
    "&display=swap"
)
GOOGLE_FONTS_RE = re.compile(r'https://fonts\.googleapis\.com/css2\?[^"\'<>]+')
GSTATIC_RE = re.compile(r"url\((https://fonts\.gstatic\.com/[^)]+)\)")

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

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


def deep_merge(base: dict, overlay: dict) -> dict:
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_merge(base[key], value)
        else:
            base[key] = value
    return base
