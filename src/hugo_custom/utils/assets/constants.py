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

# Icon names missing from the vscode-icons set, with a fallback source.
ICON_ALT = {
    "file_type_csv": ICON_ALT_BASE + "table.svg",
}

EXT_ICONS = {
    ".rs": "file_type_rust",
    ".py": "file_type_python",
    ".toml": "file_type_toml",
    ".sh": "file_type_shell",
    ".bash": "file_type_shell",
    ".js": "file_type_js",
    ".ts": "file_type_typescript",
    ".jsx": "file_type_reactjs",
    ".tsx": "file_type_reactts",
    ".json": "file_type_json",
    ".yml": "file_type_yaml",
    ".yaml": "file_type_yaml",
    ".c": "file_type_c",
    ".h": "file_type_cheader",
    ".cpp": "file_type_cpp",
    ".hpp": "file_type_cppheader",
    ".java": "file_type_java",
    ".go": "file_type_go",
    ".rb": "file_type_ruby",
    ".txt": "file_type_text",
    ".ini": "file_type_ini",
    ".cfg": "file_type_ini",
    ".sql": "file_type_sql",
    ".html": "file_type_html",
    ".css": "file_type_css",
    ".md": "file_type_markdown",
    ".ipynb": "file_type_jupyter",
    ".svg": "file_type_svg",
    ".csv": "file_type_csv",
    ".png": "file_type_image",
    ".jpg": "file_type_image",
    ".jpeg": "file_type_image",
    ".gif": "file_type_image",
    ".webp": "file_type_image",
    ".ico": "file_type_image",
    ".bmp": "file_type_image",
    ".mp4": "file_type_video",
    ".webm": "file_type_video",
    ".mov": "file_type_video",
    ".mkv": "file_type_video",
    ".avi": "file_type_video",
    ".ogv": "file_type_video",
    ".mp3": "file_type_audio",
    ".wav": "file_type_audio",
    ".ogg": "file_type_audio",
    ".flac": "file_type_audio",
    ".m4a": "file_type_audio",
    ".pdf": "file_type_pdf2",
    ".zip": "file_type_zip",
    ".xml": "file_type_xml",
}
LOCK_ICONS = {"Cargo.lock": "file_type_cargo", "uv.lock": "file_type_uv"}
DEFAULT_ICON = "default_file"

GOOGLE_FONTS_URL = (
    "https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,400;0,700;1,400"
    "&display=swap"
)
GOOGLE_FONTS_RE = re.compile(r'https://fonts\.googleapis\.com/css2\?[^"\'<>]+')
GSTATIC_RE = re.compile(r"url\((https://fonts\.gstatic\.com/[^)]+)\)")

CODE_EXTENSIONS = {
    ".rs",
    ".py",
    ".toml",
    ".sh",
    ".bash",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".json",
    ".yml",
    ".yaml",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".java",
    ".go",
    ".rb",
    ".txt",
    ".ini",
    ".cfg",
    ".sql",
    ".html",
    ".css",
    ".lock",
}

LANGS = {
    ".rs": "rust",
    ".py": "python",
    ".toml": "toml",
    ".sh": "bash",
    ".bash": "bash",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "jsx",
    ".tsx": "tsx",
    ".json": "json",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".java": "java",
    ".go": "go",
    ".rb": "ruby",
    ".txt": "text",
    ".ini": "ini",
    ".cfg": "ini",
    ".sql": "sql",
    ".html": "html",
    ".css": "css",
}

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
