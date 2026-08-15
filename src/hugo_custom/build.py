from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tomllib
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import pathspec
import tomli_w
import yaml

PACKAGE_DIR = Path(__file__).resolve().parent
TEMPLATES = PACKAGE_DIR / "templates"

CONFIG_FILENAME = "hugo_custom_site.toml"

CODE_OUTPUT_DIR = "codeview"

DEPLOY_ENV = "HUGO_DEPLOY"

CODE_EXTENSIONS = {
    ".rs", ".py", ".toml", ".sh", ".bash", ".js", ".ts", ".jsx", ".tsx",
    ".json", ".yml", ".yaml", ".c", ".h", ".cpp", ".hpp", ".java", ".go",
    ".rb", ".txt", ".ini", ".cfg", ".sql", ".html", ".css", ".lock",
}

LANGS = {
    ".rs": "rust", ".py": "python", ".toml": "toml", ".sh": "bash",
    ".bash": "bash", ".js": "javascript", ".ts": "typescript",
    ".jsx": "jsx", ".tsx": "tsx", ".json": "json", ".yml": "yaml",
    ".yaml": "yaml", ".c": "c", ".h": "c", ".cpp": "cpp", ".hpp": "cpp",
    ".java": "java", ".go": "go", ".rb": "ruby", ".txt": "text",
    ".ini": "ini", ".cfg": "ini", ".sql": "sql", ".html": "html",
    ".css": "css",
}

KATEX_VERSION = "0.18.4"
KATEX_TARBALL = f"https://registry.npmjs.org/katex/-/katex-{KATEX_VERSION}.tgz"

ICON_BASE = (
    "https://cdn.jsdelivr.net/gh/vscode-icons/vscode-icons@master/icons/"
)

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


@dataclass
class SiteConfig:
    root: Path
    source: Path
    stage: Path
    output: Path
    siteignore: Path | None
    ignore: tuple[str, ...]
    title: str
    site_url: str
    brand: str
    cache_dir: Path
    params: dict

    @property
    def vendor(self) -> Path:
        return self.cache_dir / "vendor"

    @classmethod
    def load(cls, path: Path) -> "SiteConfig":
        path = path.resolve()
        with path.open("rb") as f:
            data = tomllib.load(f)
        root = path.parent
        cache_raw = os.environ.get("HUGO_CUSTOM_CACHE") or data.get("cache-dir")
        if cache_raw:
            cache_dir = Path(cache_raw).expanduser()
            if not cache_dir.is_absolute():
                cache_dir = root / cache_dir
        else:
            base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
            cache_dir = base / "hugo_custom"
        siteignore = data.get("siteignore")
        ignore = tuple(str(p) for p in data.get("ignore", []))
        return cls(
            root=root,
            source=root / data.get("source", "self"),
            stage=root / data.get("stage", "hugo_src"),
            output=root / data.get("output", "site"),
            siteignore=(root / siteignore) if siteignore else None,
            ignore=ignore,
            title=str(data.get("title", root.name)),
            site_url=str(data.get("site-url", "")),
            brand=str(data.get("brand", root.name.upper().replace("_", " "))),
            cache_dir=cache_dir,
            params=dict(data.get("params", {})),
        )


def deep_merge(base: dict, overlay: dict) -> dict:
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_merge(base[key], value)
        else:
            base[key] = value
    return base


def find_config(start: Path) -> Path | None:
    """Locate the site configuration at the top of the repo, walking up from
    `start` (current directory) through its parents."""
    for directory in (start, *start.parents):
        candidate = directory / CONFIG_FILENAME
        if candidate.is_file():
            return candidate
    return None


def load_specs(site: SiteConfig, deploy: bool) -> list[tuple[str, pathspec.GitIgnoreSpec]]:
    specs: list[tuple[str, pathspec.GitIgnoreSpec]] = []

    def add(path: Path, base: str) -> None:
        if not path.is_file():
            return
        lines = path.read_text(encoding="utf-8").splitlines()
        if lines:
            specs.append((base, pathspec.GitIgnoreSpec.from_lines(lines)))

    add(site.root / ".gitignore", "")
    for ignore in site.source.rglob(".gitignore"):
        base = ignore.parent.relative_to(site.root).as_posix()
        add(ignore, base)
    if deploy and site.siteignore is not None:
        add(site.siteignore, "")
    if site.ignore:
        specs.append(("", pathspec.GitIgnoreSpec.from_lines(site.ignore)))
    return specs


def is_ignored(rel_from_root: str, specs: list[tuple[str, pathspec.GitIgnoreSpec]]) -> bool:
    for base, spec in specs:
        if base:
            if rel_from_root != base and not rel_from_root.startswith(f"{base}/"):
                continue
            local = rel_from_root[len(base):].lstrip("/")
        else:
            local = rel_from_root
        if spec.match_file(local):
            return True
    return False


def write_if_changed(dst: Path, content: str) -> None:
    if dst.is_file() and dst.read_text(encoding="utf-8") == content:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(content, encoding="utf-8")


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
                rel = member.name[len("package/dist/"):]
                if rel in ("katex.min.js", "katex.min.css") or rel.startswith(
                    ("fonts/", "contrib/")
                ):
                    member.name = rel
                    tar.extract(member, tmp, filter="data")
    except Exception as exc:
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
    if (cache / "lato.css").is_file() and any(
        (cache / "lato").glob("*.woff2")
    ):
        return cache
    tmp = cache.with_suffix(".tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    (tmp / "lato").mkdir(parents=True)

    def fetch(url: str) -> bytes:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
                )
            },
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.read()

    try:
        css = fetch(GOOGLE_FONTS_URL).decode()
    except Exception as exc:
        shutil.rmtree(tmp, ignore_errors=True)
        sys.exit(f"Lato fonts are not cached in {cache} and fetching {GOOGLE_FONTS_URL} failed: {exc}")

    def localize(match: re.Match) -> str:
        url = match.group(1)
        name = url.rsplit("/", 1)[-1].split("?")[0]
        dest = tmp / "lato" / name
        if not dest.is_file():
            try:
                dest.write_bytes(fetch(url))
            except Exception as exc:
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
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
                )
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
        except Exception:
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


def collect(site: SiteConfig, specs: list[tuple[str, pathspec.GitIgnoreSpec]]) -> list[Path]:
    published: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(site.source):
        kept_dirs = []
        for d in dirnames:
            if d == ".git":
                continue
            rel_root = (Path(dirpath) / d).relative_to(site.root).as_posix()
            if not is_ignored(rel_root, specs):
                kept_dirs.append(d)
        dirnames[:] = kept_dirs
        for f in filenames:
            if f in (".gitignore", ".siteignore", "__init__.py"):
                continue
            rel_root = (Path(dirpath) / f).relative_to(site.root).as_posix()
            if not is_ignored(rel_root, specs):
                published.append(Path(dirpath) / f)
    return published


def rel_of(site: SiteConfig, path: Path) -> str:
    return path.relative_to(site.source).as_posix()


def url_rel(rel: str) -> str:
    """Strip leading dots from path segments so Hugo renders them (hidden
    files and directories are skipped by Hugo)."""
    return "/".join(seg.lstrip(".") for seg in rel.split("/"))


def git_date(site: SiteConfig, path: Path, first: bool) -> str | None:
    if first:
        cmd = ["git", "log", "--diff-filter=A", "--format=%aI", "--", str(path)]
    else:
        cmd = ["git", "log", "-1", "--format=%aI", "--", str(path)]
    try:
        out = subprocess.run(
            cmd, cwd=site.root, capture_output=True, text=True, check=False
        ).stdout.strip()
    except OSError:
        return None
    return out[:10] if out else None


def humanize(name: str) -> str:
    return " ".join(w[:1].upper() + w[1:] for w in re.split(r"[_\-]+", name))


def slugify(tag: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", tag.lower()).strip("-")


def extract_tags(text: str) -> list[str]:
    tags: list[str] = []
    lines = text.split("\n")
    i = 0
    keyword_re = re.compile(r"^#{2,4}\s*[Kk]eywords\.?\s*:?\s*$")
    while i < len(lines):
        if keyword_re.match(lines[i].strip()):
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            while j < len(lines) and lines[j].strip() and not lines[j].lstrip().startswith("#"):
                tag = re.sub(r"^\s*[-*]\s*", "", lines[j]).strip()
                tag = re.sub(r"[.,;:]+$", "", tag)
                if tag:
                    tags.append(tag)
                j += 1
            i = j
        else:
            i += 1
    return tags


def split_front_matter(text: str) -> tuple[dict | None, str]:
    if not text.startswith("---"):
        return None, text
    lines = text.split("\n", 2)
    if len(lines) < 3 or lines[1].strip() != "---":
        return None, text
    fm_text = lines[1]
    try:
        meta = yaml.safe_load(fm_text)
    except yaml.YAMLError:
        return None, text
    if not isinstance(meta, dict):
        return None, text
    rest = text[len("---\n") + len(fm_text) + len("\n---\n"):]
    return meta, rest


def front_matter(meta: dict) -> str:
    dump = yaml.safe_dump(
        meta, sort_keys=False, allow_unicode=True, default_flow_style=False
    ).rstrip()
    return f"---\n{dump}\n---\n\n"


def split_title(body: str) -> tuple[str | None, str]:
    """Return the first heading (any level, like Quarto's title rule) and the
    body without it. A leading front-matter block is skipped."""
    lines = body.split("\n")
    start = 0
    if lines and lines[0].strip() == "---":
        start = 1
        while start < len(lines) and lines[start].strip() != "---":
            start += 1
        start += 1
    for i in range(start, len(lines)):
        m = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", lines[i])
        if m and m.group(1).strip():
            return m.group(1).strip(), "\n".join(lines[:i] + lines[i + 1:])
    return None, body


def ipynb_to_markdown(nb: dict) -> str:
    """Convert notebook cells to markdown without executing anything:
    markdown cells pass through, code cells become fenced blocks and stored
    text/image outputs are kept as-is."""
    lang = (
        (nb.get("metadata") or {}).get("kernelspec", {}).get("language", "python")
    )
    out: list[str] = []
    for cell in nb.get("cells", []):
        ctype = cell.get("cell_type")
        source = "".join(cell.get("source", []))
        if ctype == "markdown":
            out.append(source)
            out.append("")
        elif ctype == "code":
            code = source.rstrip()
            if code:
                run = max((len(m) for m in re.findall(r"`+", code)), default=0)
                fence = "`" * max(3, run + 1)
                out.append(f"{fence}{lang}")
                out.append(code)
                out.append(fence)
                out.append("")
            for output in cell.get("outputs", []):
                otype = output.get("output_type")
                if otype in ("stream", "execute_result", "display_data"):
                    if otype == "stream":
                        text = "".join(output.get("text", []))
                    else:
                        data = output.get("data") or {}
                        text = "".join(data.get("text/plain") or [])
                    if text and text.strip():
                        out.append("```")
                        out.append(text.rstrip())
                        out.append("```")
                        out.append("")
                    data = output.get("data") or {}
                    for mime, payload in data.items():
                        if mime.startswith("image/") and isinstance(payload, str):
                            out.append(f"![]({mime}:base64,{payload})")
                            out.append("")
    return "\n".join(out)


class Builder:
    def __init__(self, site: SiteConfig, deploy: bool, preview_mode: bool = False):
        self.site = site
        self.deploy = deploy
        self.preview_mode = preview_mode
        self.specs = load_specs(site, deploy)
        self.published = collect(site, self.specs)
        self.published_rels = {rel_of(site, p) for p in self.published}
        self.pages: list[tuple[str, list[str], str]] = []

    # ---------- staging ----------

    def stage(self) -> None:
        stage, site = self.site.stage, self.site
        stage.mkdir(parents=True, exist_ok=True)
        (stage / "content").mkdir(parents=True, exist_ok=True)
        (stage / "static").mkdir(parents=True, exist_ok=True)
        content_expected: set[str] = set()
        static_expected: set[str] = set()
        for src in self.published:
            rel = rel_of(site, src)
            urel = url_rel(rel)
            ext = src.suffix.lower()
            if ext == ".md":
                content_expected.add(urel)
                self.write_page(src)
            elif ext == ".ipynb":
                content_expected.add(f"{urel}.md")
                self.write_notebook(src)
            elif ext in CODE_EXTENSIONS:
                content_expected.add(f"{CODE_OUTPUT_DIR}/{urel}.md")
                static_expected.add(urel)
                self.copy_raw(src)
                self.write_codeview(src)
            else:
                static_expected.add(urel)
                self.copy_raw(src)
        self.clean_content(content_expected)
        self.clean_static(static_expected)
        self.stage_assets()
        self.stage_sidebar()
        self.stage_config()

    def write_page(self, src: Path) -> None:
        site = self.site
        rel = rel_of(site, src)
        text = src.read_text(encoding="utf-8")
        meta, body = split_front_matter(text)
        if meta is None:
            meta = {}
        created = git_date(site, src, first=True)
        modified = git_date(site, src, first=False)
        if created is None and modified is not None:
            created = modified
        if created:
            meta.setdefault("date", created)
        if modified:
            meta["lastmod"] = modified
        tags = meta.get("categories") or meta.get("keywords") or meta.get("tags") or []
        if isinstance(tags, str):
            tags = [tags]
        tags = [str(t) for t in tags]
        for tag in extract_tags(body):
            if tag not in tags:
                tags.append(tag)
        meta.pop("categories", None)
        meta.pop("keywords", None)
        if tags:
            meta["tags"] = tags
        parts = rel.split("/")
        if len(parts) > 1:
            meta.setdefault("image", f"{site.site_url}og/{slugify(parts[0])}.png")
        if "title" not in meta:
            title, body = split_title(body)
            if title:
                meta["title"] = title
        self.pages.append((rel, tags, created or ""))
        write_if_changed(site.stage / "content" / url_rel(rel), front_matter(meta) + body)

    def write_notebook(self, src: Path) -> None:
        site = self.site
        rel = rel_of(site, src)
        nb = json.loads(src.read_text(encoding="utf-8"))
        nb_meta = nb.get("metadata") or {}
        meta: dict = {}
        if nb_meta.get("title"):
            meta["title"] = str(nb_meta["title"])
        else:
            meta["title"] = humanize(src.stem)
        created = git_date(site, src, first=True)
        modified = git_date(site, src, first=False)
        if created is None and modified is not None:
            created = modified
        if created:
            meta["date"] = created
        if modified:
            meta["lastmod"] = modified
        tags = nb_meta.get("categories") or nb_meta.get("tags") or []
        if isinstance(tags, str):
            tags = [tags]
        tags = [str(t) for t in tags]
        if tags:
            meta["tags"] = tags
        parts = rel.split("/")
        if len(parts) > 1:
            meta["image"] = f"{site.site_url}og/{slugify(parts[0])}.png"
        self.pages.append((rel, tags, created or ""))
        body = ipynb_to_markdown(nb)
        write_if_changed(
            site.stage / "content" / f"{url_rel(rel)}.md", front_matter(meta) + body
        )

    def write_codeview(self, src: Path) -> None:
        site = self.site
        rel = url_rel(rel_of(site, src))
        try:
            src.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return
        lang = LANGS.get(src.suffix.lower(), "text")
        if src.name in ("Cargo.lock", "uv.lock") and src.suffix.lower() == ".lock":
            lang = "toml"
        # With pretty URLs the codeview page lives at /codeview/<rel>/, one
        # level deeper than the raw file's directory.
        page_dir = os.path.join(CODE_OUTPUT_DIR, str(Path(rel).parent), Path(rel).name)
        download = os.path.relpath(rel, page_dir)
        meta = {"title": src.name, "rel": rel, "lang": lang, "download": download}
        write_if_changed(
            site.stage / "content" / CODE_OUTPUT_DIR / f"{rel}.md",
            front_matter(meta),
        )
        self.pages.append((f"{CODE_OUTPUT_DIR}/{rel}", [], ""))

    def copy_raw(self, src: Path) -> None:
        site = self.site
        dst = site.stage / "static" / url_rel(rel_of(site, src))
        if (
            not dst.exists()
            or dst.stat().st_size != src.stat().st_size
            or dst.stat().st_mtime_ns != src.stat().st_mtime_ns
        ):
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    def clean_content(self, expected: set[str]) -> None:
        content = self.site.stage / "content"
        if not content.is_dir():
            return
        for dirpath, dirnames, filenames in os.walk(content):
            rel_dir = Path(dirpath).relative_to(content).as_posix()
            for f in filenames:
                key = f if rel_dir == "." else f"{rel_dir}/{f}"
                if key not in expected:
                    (Path(dirpath) / f).unlink()

    def clean_static(self, expected: set[str]) -> None:
        static = self.site.stage / "static"
        if not static.is_dir():
            return
        protected = {"og", "icons", "vendor", "css", "js"}
        for dirpath, dirnames, filenames in os.walk(static):
            dirnames[:] = [d for d in dirnames if d not in protected]
            rel_dir = Path(dirpath).relative_to(static).as_posix()
            for f in filenames:
                key = f if rel_dir == "." else f"{rel_dir}/{f}"
                if key not in expected:
                    (Path(dirpath) / f).unlink()
        for dirpath, dirnames, filenames in os.walk(static, topdown=False):
            for d in dirnames:
                if d in protected:
                    continue
                p = Path(dirpath) / d
                if p.is_dir() and not any(p.iterdir()):
                    p.rmdir()

    def icon_for(self, src: Path) -> str | None:
        ext = src.suffix.lower()
        if ext == ".md":
            return EXT_ICONS[".md"]
        if ext == ".ipynb":
            return EXT_ICONS[".ipynb"]
        if ext in CODE_EXTENSIONS:
            return LOCK_ICONS.get(src.name) or EXT_ICONS.get(ext, DEFAULT_ICON)
        return None

    def stage_assets(self) -> None:
        site = self.site
        stage = site.stage
        og_dir = stage / "static" / "og"
        og_dir.mkdir(parents=True, exist_ok=True)
        projects = sorted(
            {rel_of(site, p).split("/")[0] for p in self.published if "/" in rel_of(site, p)}
        )
        wanted = {f"{slugify(project)}.png" for project in projects}
        for stale in og_dir.glob("*.png"):
            if stale.name not in wanted:
                stale.unlink()
        for project in projects:
            img = og_dir / f"{slugify(project)}.png"
            if not img.exists():
                self.make_og(img, humanize(project))
        katex = ensure_katex(site.vendor)
        shutil.copytree(katex, stage / "static" / "vendor" / "katex", dirs_exist_ok=True)
        fonts = ensure_fonts(site.vendor)
        shutil.copytree(fonts, stage / "static" / "vendor" / "fonts", dirs_exist_ok=True)
        needed_icons = {icon for icon in (self.icon_for(p) for p in self.published) if icon}
        icons = ensure_file_icons(needed_icons, site.vendor)
        shutil.copytree(icons, stage / "static" / "icons", dirs_exist_ok=True)
        shutil.copytree(TEMPLATES / "layouts", stage / "layouts", dirs_exist_ok=True)
        for rel in ("css", "js"):
            dst = stage / "static" / rel
            dst.mkdir(parents=True, exist_ok=True)
            for f in (TEMPLATES / "static" / rel).glob("*"):
                write_if_changed(dst / f.name, f.read_text(encoding="utf-8"))

    def make_og(self, path: Path, label: str) -> None:
        from PIL import Image, ImageDraw, ImageFont

        width, height = 1200, 630
        digest = hashlib.sha256(str(path.stem).encode()).hexdigest()
        bg = tuple(int(digest[i:i + 2], 16) for i in (0, 2, 4))
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
            if current and draw.textlength(current + " " + word, font=title_font) > width - 160:
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
        brand = self.site.brand
        brand_width = draw.textlength(brand, font=small_font)
        draw.text(((width - brand_width) / 2, height - 90), brand, font=small_font, fill=(230, 230, 230))
        img.save(path, format="PNG")

    def tree(self) -> dict:
        site = self.site
        tree: dict = {"dirs": {}, "files": []}

        def add(parts: list[str], kind: str, href: str, icon: str | None) -> None:
            node = tree
            for part in parts[:-1]:
                node = node["dirs"].setdefault(part, {"dirs": {}, "files": []})
            node["files"].append((kind, parts[-1], href, icon))

        for p in sorted(self.published, key=lambda x: rel_of(site, x).lower()):
            rel = url_rel(rel_of(site, p))
            ext = p.suffix.lower()
            parts = rel.split("/")
            if ext == ".md":
                add(parts, "md", "/" + rel[: -len(".md")] + "/", EXT_ICONS[".md"])
            elif ext == ".ipynb":
                add(parts, "nb", "/" + rel + "/", EXT_ICONS[".ipynb"])
            elif ext in CODE_EXTENSIONS:
                icon = LOCK_ICONS.get(p.name) or EXT_ICONS.get(ext, DEFAULT_ICON)
                add(parts, "code", f"/{CODE_OUTPUT_DIR}/{rel}/", icon)
            else:
                add(parts, "file", "/" + rel, None)
        return tree

    def sidebar_entries(self) -> list[dict]:
        tree = self.tree()
        out: list[dict] = [{"href": "/", "text": self.site.title}]

        def file_entry(kind: str, name: str, href: str, icon: str | None) -> dict:
            entry: dict = {"href": href, "text": name, "kind": kind}
            if icon:
                entry["icon"] = icon
            return entry

        def section(label: str, node: dict) -> dict | None:
            entry: dict = {"section": label, "contents": []}
            for name, child in sorted(node["dirs"].items(), key=lambda kv: kv[0].lower()):
                sub = section(humanize(name), child)
                if sub is not None:
                    entry["contents"].append(sub)
            page_files = [f for f in node["files"] if f[0] != "file"]
            for kind, name, href, icon in sorted(page_files, key=lambda f: f[1].lower()):
                entry["contents"].append(file_entry(kind, name, href, icon))
            return entry if entry["contents"] else None

        for name, node in sorted(tree["dirs"].items(), key=lambda kv: kv[0].lower()):
            item = section(humanize(name), node)
            if item is not None:
                out.append(item)
        page_files = [f for f in tree["files"] if f[0] != "file"]
        for kind, name, href, icon in sorted(page_files, key=lambda f: f[1].lower()):
            out.append(file_entry(kind, name, href, icon))
        out.append({"href": "/tags/", "text": "Tags"})
        return out

    def stage_sidebar(self) -> None:
        data = {"entries": self.sidebar_entries()}
        write_if_changed(
            self.site.stage / "data" / "sidebar.yml",
            yaml.safe_dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False),
        )

    def stage_config(self) -> None:
        site = self.site
        cfg = tomllib.loads((TEMPLATES / "hugo.toml").read_text(encoding="utf-8"))
        cfg["title"] = site.title
        cfg["baseURL"] = site.site_url
        cfg["params"] = deep_merge(cfg.get("params") or {}, site.params)
        write_if_changed(site.stage / "hugo.toml", tomli_w.dumps(cfg))

    # ---------- rendering ----------

    def render(self) -> None:
        site = self.site
        if site.output.exists():
            shutil.rmtree(site.output)
        result = subprocess.run(
            ["hugo", "--source", str(site.stage), "--destination", str(site.output)],
            cwd=site.root, text=True, check=False,
        )
        if result.returncode != 0:
            sys.exit(f"hugo build failed with exit code {result.returncode}")

    def preview(self) -> None:
        site = self.site
        subprocess.run(
            [
                "hugo", "server",
                "--source", str(site.stage),
                "--destination", str(site.output),
            ],
            cwd=site.root, check=False,
        )

    def summary(self) -> None:
        site = self.site
        n_pages = len(list(site.output.rglob("*.html")))
        n_code = sum(1 for rel, _, _ in self.pages if rel.startswith(CODE_OUTPUT_DIR))
        n_md = sum(1 for rel, _, _ in self.pages if rel.endswith(".md"))
        n_tags = len({slugify(t) for _, tags, _ in self.pages for t in tags})
        print(f"rendered {n_pages} pages ({n_md} markdown, {n_code} code views), {n_tags} tags")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Stage a content folder into a Hugo site project, build it and "
            "vendor runtime assets (KaTeX, fonts, icons)."
        )
    )
    parser.add_argument(
        "-c", "--config", default=None,
        help=(
            f"path to the {CONFIG_FILENAME} configuration (default: "
            f"{CONFIG_FILENAME} at the top of the repo, found by walking up "
            "from the current directory)"
        ),
    )
    parser.add_argument("--deploy", action="store_true", help="apply .siteignore exclusions")
    parser.add_argument("--stage-only", action="store_true", help="build the staged hugo project without rendering")
    parser.add_argument("--preview", action="store_true", help="stage then run hugo server on the staged project")
    args = parser.parse_args()

    config_path = Path(args.config) if args.config else find_config(Path.cwd())
    if config_path is None:
        sys.exit(
            f"no {CONFIG_FILENAME} found in {Path.cwd()} or any parent directory"
        )
    deploy = args.deploy or os.environ.get(DEPLOY_ENV, "").lower() == "true"

    site = SiteConfig.load(config_path)
    builder = Builder(site, deploy, preview_mode=args.preview)
    builder.stage()
    print(
        f"staged {len(builder.published)} published files from {site.source} into {site.stage}"
    )
    if args.stage_only:
        return
    if args.preview:
        builder.preview()
    else:
        builder.render()
        builder.summary()


if __name__ == "__main__":
    main()