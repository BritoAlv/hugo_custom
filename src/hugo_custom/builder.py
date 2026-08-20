from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import tomli_w
import yaml

from hugo_custom.assets import (
    CODE_EXTENSIONS,
    DEFAULT_ICON,
    EXT_ICONS,
    LANGS,
    LOCK_ICONS,
    ensure_file_icons,
    ensure_fonts,
    ensure_katex,
    make_og,
)
from hugo_custom.config import SiteConfig, deep_merge
from hugo_custom.files import collect, load_specs, rel_of, url_rel
from hugo_custom.git import git_date
from hugo_custom.markdown import (
    csv_to_markdown,
    extract_tags,
    front_matter,
    humanize,
    ipynb_to_markdown,
    slugify,
    split_front_matter,
    split_title,
)

PACKAGE_DIR = Path(__file__).resolve().parent
TEMPLATES = PACKAGE_DIR / "templates"

CODE_OUTPUT_DIR = "codeview"

PREVIEW_OUTPUT_DIR = "preview"

PREVIEW_KINDS = {
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


def lan_ip() -> str:
    """Best-effort detection of the machine's primary LAN IPv4 address."""
    import socket

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return ""

FENCE_RE = re.compile(r"^\s*(```|~~~)")
LINK_RE = re.compile(r"\]\(([^)]+)\)")


def rebase_links(body: str, base_dir: str) -> str:
    """Rewrite relative link destinations in markdown `body` so they resolve
    from `base_dir` (the homepage file's original folder). Skips fenced code
    blocks; absolute, external and fragment-only destinations are left as-is."""
    if not base_dir:
        return body

    def rebase(match: re.Match) -> str:
        dest = match.group(1)
        if dest[0:1] in ("#", "/") or dest.startswith(
            ("http://", "https://", "mailto:", "data:")
        ):
            return match.group(0)
        return f"]({base_dir}/{dest})"

    out: list[str] = []
    in_fence = ""
    for line in body.splitlines(keepends=True):
        fence = FENCE_RE.match(line)
        if fence:
            marker = fence.group(1)
            if not in_fence:
                in_fence = marker
            elif line.strip().startswith(marker):
                in_fence = ""
        if not in_fence:
            line = LINK_RE.sub(rebase, line)
        out.append(line)
    return "".join(out)


def write_if_changed(dst: Path, content: str) -> None:
    if dst.is_file() and dst.read_text(encoding="utf-8") == content:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(content, encoding="utf-8")


def chroma_css(style: str, prefix: str) -> str:
    """Generate Chroma CSS for `style` scoped under `prefix` so code colors
    follow the site's light/dark theme (manual `data-theme` wins over the
    OS preference, mirroring main.css)."""
    result = subprocess.run(
        ["hugo", "gen", "chromastyles", "--style", style],
        capture_output=True,
        text=True,
        check=False,
    )
    css = result.stdout
    css = css.replace(".chroma", f"{prefix} .chroma")
    css = css.replace(".bg {", f"{prefix} .bg {{")
    return css


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
                if src.suffix.lower() in PREVIEW_KINDS:
                    content_expected.add(f"{PREVIEW_OUTPUT_DIR}/{urel}.md")
                    self.write_preview(src)
        home_staged = self.stage_homepage()
        if home_staged:
            content_expected.add("_index.md")
        self.clean_content(content_expected)
        self.clean_static(static_expected)
        self.stage_assets()
        self.stage_sidebar()
        self.stage_config()

    def stage_homepage(self) -> bool:
        """Stage the configured homepage file as content/_index.md so the
        site's index page renders it. Returns True when staged."""
        site = self.site
        if not site.homepage:
            return False
        rel = site.homepage
        src = site.source / rel
        if not src.is_file() or src.suffix.lower() != ".md":
            print(
                f"warning: homepage file {rel!r} not found in source (must be a .md file)",
                file=sys.stderr,
            )
            return False
        if rel not in self.published_rels:
            print(
                f"warning: homepage file {rel!r} is not published in this build",
                file=sys.stderr,
            )
            return False
        text = src.read_text(encoding="utf-8")
        meta, body = split_front_matter(text)
        if meta is None:
            meta = {}
        meta.setdefault("title", site.title)
        meta.pop("rel", None)
        body = rebase_links(body, str(Path(rel).parent))
        write_if_changed(
            site.stage / "content" / "_index.md", front_matter(meta) + body
        )
        return True

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
        write_if_changed(
            site.stage / "content" / url_rel(rel), front_matter(meta) + body
        )

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

    def write_preview(self, src: Path) -> None:
        site = self.site
        rel = url_rel(rel_of(site, src))
        kind = PREVIEW_KINDS[src.suffix.lower()]
        # With pretty URLs the preview page lives at /preview/<rel>/, one
        # level deeper than the raw file's directory.
        page_dir = os.path.join(
            PREVIEW_OUTPUT_DIR, str(Path(rel).parent), Path(rel).name
        )
        download = os.path.relpath(rel, page_dir)
        meta = {
            "title": src.name,
            "rel": rel,
            "kind": kind,
            "download": download,
        }
        body = ""
        if kind in ("csv", "text"):
            try:
                text = src.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                text = ""
            body = csv_to_markdown(text) if kind == "csv" else f"```text\n{text}\n```"
        write_if_changed(
            site.stage / "content" / PREVIEW_OUTPUT_DIR / f"{rel}.md",
            front_matter(meta) + body,
        )
        self.pages.append((f"{PREVIEW_OUTPUT_DIR}/{rel}", [], ""))

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
        return EXT_ICONS.get(ext, DEFAULT_ICON)

    def stage_assets(self) -> None:
        site = self.site
        stage = site.stage
        og_dir = stage / "static" / "og"
        og_dir.mkdir(parents=True, exist_ok=True)
        projects = sorted(
            {
                rel_of(site, p).split("/")[0]
                for p in self.published
                if "/" in rel_of(site, p)
            }
        )
        wanted = {f"{slugify(project)}.png" for project in projects}
        for stale in og_dir.glob("*.png"):
            if stale.name not in wanted:
                stale.unlink()
        for project in projects:
            img = og_dir / f"{slugify(project)}.png"
            if not img.exists():
                make_og(img, humanize(project), site.brand)
        katex = ensure_katex(site.vendor)
        shutil.copytree(
            katex, stage / "static" / "vendor" / "katex", dirs_exist_ok=True
        )
        fonts = ensure_fonts(site.vendor)
        shutil.copytree(
            fonts, stage / "static" / "vendor" / "fonts", dirs_exist_ok=True
        )
        needed_icons = {
            icon for icon in (self.icon_for(p) for p in self.published) if icon
        }
        icons = ensure_file_icons(needed_icons, site.vendor)
        shutil.copytree(icons, stage / "static" / "icons", dirs_exist_ok=True)
        shutil.copytree(TEMPLATES / "layouts", stage / "layouts", dirs_exist_ok=True)
        dst = stage / "static" / "css"
        dst.mkdir(parents=True, exist_ok=True)
        for f in (TEMPLATES / "static" / "css").glob("*"):
            write_if_changed(dst / f.name, f.read_text(encoding="utf-8"))
        self.stage_js()
        write_if_changed(
            stage / "static" / "css" / "chroma.css",
            chroma_css("github", ':root:not([data-theme="dark"])')
            + "\n"
            + chroma_css("github-dark", ':root[data-theme="dark"]'),
        )

    def tsc_cmd(self) -> list[str] | None:
        local = PACKAGE_DIR.parents[1] / "node_modules" / ".bin" / "tsc"
        if local.is_file():
            return [str(local)]
        if shutil.which("pnpm"):
            return ["pnpm", "dlx", "--package=typescript", "tsc"]
        if shutil.which("tsc"):
            return ["tsc"]
        return None

    def stage_js(self) -> None:
        site = self.site
        out = site.stage / "static" / "js"
        if out.is_dir():
            shutil.rmtree(out)
        out.mkdir(parents=True)
        cmd = self.tsc_cmd()
        if cmd is None:
            sys.exit(
                "error: TypeScript compiler not found; install Node.js and pnpm "
                "(`pnpm dlx --package=typescript tsc`) or put tsc on PATH"
            )
        print(f"compiling TypeScript templates -> {out}")
        proc = subprocess.run(
            [
                *cmd,
                "--project",
                str(TEMPLATES / "static" / "ts" / "tsconfig.json"),
                "--outDir",
                str(out),
            ],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            sys.exit(proc.stdout + proc.stderr)

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
                if ext in PREVIEW_KINDS:
                    add(
                        parts,
                        "file",
                        f"/{PREVIEW_OUTPUT_DIR}/{rel}/",
                        EXT_ICONS.get(ext) or DEFAULT_ICON,
                    )
                else:
                    add(parts, "file", "/" + rel, EXT_ICONS.get(ext) or DEFAULT_ICON)
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
            for name, child in sorted(
                node["dirs"].items(), key=lambda kv: kv[0].lower()
            ):
                sub = section(humanize(name), child)
                if sub is not None:
                    entry["contents"].append(sub)
            page_files = sorted(node["files"], key=lambda f: f[1].lower())
            for kind, name, href, icon in page_files:
                entry["contents"].append(file_entry(kind, name, href, icon))
            return entry if entry["contents"] else None

        for name, node in sorted(tree["dirs"].items(), key=lambda kv: kv[0].lower()):
            item = section(humanize(name), node)
            if item is not None:
                out.append(item)
        page_files = sorted(tree["files"], key=lambda f: f[1].lower())
        for kind, name, href, icon in page_files:
            out.append(file_entry(kind, name, href, icon))
        out.append({"href": "/tags/", "text": "Tags"})
        return out

    def stage_sidebar(self) -> None:
        data = {"entries": self.sidebar_entries()}
        write_if_changed(
            self.site.stage / "data" / "sidebar.yml",
            yaml.safe_dump(
                data, sort_keys=False, allow_unicode=True, default_flow_style=False
            ),
        )

    def stage_config(self) -> None:
        site = self.site
        cfg = tomllib.loads((TEMPLATES / "hugo.toml").read_text(encoding="utf-8"))
        cfg["title"] = site.title
        cfg["baseURL"] = site.site_url
        cfg["params"] = deep_merge(cfg.get("params") or {}, site.params)
        if site.homepage:
            cfg["params"]["homepage"] = site.homepage
        write_if_changed(site.stage / "hugo.toml", tomli_w.dumps(cfg))

    # ---------- rendering ----------

    def render(self) -> None:
        site = self.site
        if site.output.exists():
            shutil.rmtree(site.output)
        result = subprocess.run(
            ["hugo", "--source", str(site.stage), "--destination", str(site.output)],
            cwd=site.root,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            sys.exit(f"hugo build failed with exit code {result.returncode}")

    def preview(self, host: str = "127.0.0.1") -> None:
        site = self.site
        cmd = [
            "hugo",
            "server",
            "--source",
            str(site.stage),
            "--destination",
            str(site.output),
            "--bind",
            host,
            "--liveReloadPort",
            "1313",
        ]
        if host not in ("127.0.0.1", "localhost"):
            cmd += ["--baseURL", f"http://{host}:1313"]
        if host in ("0.0.0.0", ""):
            ip = lan_ip()
            if ip:
                print(f"On your phone (same WiFi), open: http://{ip}:1313/", flush=True)
        subprocess.run(cmd, cwd=site.root, check=False)

    def summary(self) -> None:
        site = self.site
        n_pages = len(list(site.output.rglob("*.html")))
        n_code = sum(1 for rel, _, _ in self.pages if rel.startswith(CODE_OUTPUT_DIR))
        n_md = sum(1 for rel, _, _ in self.pages if rel.endswith(".md"))
        n_tags = len({slugify(t) for _, tags, _ in self.pages for t in tags})
        print(
            f"rendered {n_pages} pages ({n_md} markdown, {n_code} code views), {n_tags} tags"
        )
