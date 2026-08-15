from __future__ import annotations

import hashlib
import io
import os
import re
import shutil
import sys
import tarfile
import urllib.request
from pathlib import Path

KATEX_VERSION = "0.18.4"
KATEX_TARBALL = f"https://registry.npmjs.org/katex/-/katex-{KATEX_VERSION}.tgz"

ICON_BASE = "https://cdn.jsdelivr.net/gh/vscode-icons/vscode-icons@master/icons/"

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


def ensure_katex(vendor: Path) -> Path:
    """Return a directory with the pinned KaTeX assets, downloading and caching if needed."""
    cache = vendor / "katex"
    fonts = cache / "fonts"
    if (
        (cache / "katex.min.js").is_file()
        and (cache / "katex.min.css").is_file()
        and (cache / "contrib" / "auto-render.min.js").is_file()
        and fonts.is_dir()
        and len(list(fonts.glob("*.woff2"))) >= 10
    ):
        return cache
    tmp = cache.with_suffix(".tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    try:
        with urllib.request.urlopen(KATEX_TARBALL, timeout=120) as resp:
            data = resp.read()
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
            for member in tar.getmembers():
                if not member.name.startswith("package/dist/"):
                    continue
                rel = member.name[len("package/dist/") :]
                if rel in ("katex.min.js", "katex.min.css") or rel.startswith(
                    ("fonts/", "contrib/")
                ):
                    member.name = rel
                    tar.extract(member, tmp, filter="data")
    except (OSError, tarfile.TarError) as exc:
        shutil.rmtree(tmp, ignore_errors=True)
        sys.exit(
            f"KaTeX assets are not cached in {cache} and fetching {KATEX_TARBALL} "
            f"failed: {exc}"
        )
    shutil.rmtree(cache, ignore_errors=True)
    os.replace(tmp, cache)
    print(f"fetched KaTeX {KATEX_VERSION} into {cache}")
    return cache


def ensure_fonts(vendor: Path) -> Path:
    """Return a directory with Lato woff2 + a local @font-face stylesheet, cached on disk."""
    cache = vendor / "fonts"
    if (cache / "lato.css").is_file() and any((cache / "lato").glob("*.woff2")):
        return cache
    tmp = cache.with_suffix(".tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    (tmp / "lato").mkdir(parents=True)

    def fetch(url: str) -> bytes:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.read()

    try:
        css = fetch(GOOGLE_FONTS_URL).decode()
    except OSError as exc:
        shutil.rmtree(tmp, ignore_errors=True)
        sys.exit(
            f"Lato fonts are not cached in {cache} and fetching {GOOGLE_FONTS_URL} failed: {exc}"
        )

    def localize(match: re.Match) -> str:
        url = match.group(1)
        name = url.rsplit("/", 1)[-1].split("?")[0]
        dest = tmp / "lato" / name
        if not dest.is_file():
            try:
                dest.write_bytes(fetch(url))
            except OSError as exc:
                shutil.rmtree(tmp, ignore_errors=True)
                sys.exit(f"failed to fetch font {url}: {exc}")
        return f"lato/{name}"

    css = GSTATIC_RE.sub(lambda m: f"url({localize(m)})", css)
    (tmp / "lato.css").write_text(css)
    shutil.rmtree(cache, ignore_errors=True)
    os.replace(tmp, cache)
    print(f"fetched Lato fonts into {cache}")
    return cache


def ensure_file_icons(names: set[str], vendor: Path) -> Path:
    """Return the cache dir with per-extension SVGs, fetching missing ones from
    the vscode-icons set (cached on disk; failed fetches fall back to the
    generic file icon)."""
    cache = vendor / "icons"
    cache.mkdir(parents=True, exist_ok=True)
    wanted = names | {DEFAULT_ICON}
    fetched = {p.name.removesuffix(".svg") for p in cache.glob("*.svg")}
    missing = wanted - fetched
    if not missing:
        return cache

    def fetch(name: str) -> str | None:
        req = urllib.request.Request(
            ICON_BASE + name + ".svg",
            headers={"User-Agent": USER_AGENT},
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
        except OSError:
            return None
        if resp.status != 200 or not data.strip():
            return None
        return data.decode("utf-8")

    for name in sorted(missing):
        data = fetch(name)
        if data is None:
            print(f"warning: could not fetch icon {name}, using {DEFAULT_ICON}.svg")
            if name == DEFAULT_ICON:
                cache.mkdir(parents=True, exist_ok=True)
                (cache / f"{name}.svg").write_text(
                    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"></svg>',
                    encoding="utf-8",
                )
            continue
        (cache / f"{name}.svg").write_text(data, encoding="utf-8")
    print(f"fetched {sorted(missing)} icons into {cache}")
    return cache


def make_og(path: Path, label: str, brand: str) -> None:
    from PIL import Image, ImageDraw, ImageFont

    width, height = 1200, 630
    digest = hashlib.sha256(str(path.stem).encode()).hexdigest()
    bg = tuple(int(digest[i : i + 2], 16) for i in (0, 2, 4))
    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    title_font = None
    small_font = None
    for fp in font_paths:
        if os.path.exists(fp):
            title_font = ImageFont.truetype(fp, 96)
            small_font = ImageFont.truetype(fp, 40)
            break
    if title_font is None:
        title_font = ImageFont.load_default(size=64)
        small_font = ImageFont.load_default(size=32)
    words = label.split()
    lines = []
    current = ""
    for word in words:
        if (
            current
            and draw.textlength(current + " " + word, font=title_font) > width - 160
        ):
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    y = height // 2 - 40 * max(1, len(lines) // 2)
    primer = (255, 255, 255)
    for line in lines[:4]:
        text_width = draw.textlength(line, font=title_font)
        draw.text(((width - text_width) / 2, y), line, font=title_font, fill=primer)
        y += 110
    brand_width = draw.textlength(brand, font=small_font)
    draw.text(
        ((width - brand_width) / 2, height - 90),
        brand,
        font=small_font,
        fill=(230, 230, 230),
    )
    img.save(path, format="PNG")
