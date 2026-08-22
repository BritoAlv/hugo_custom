from __future__ import annotations

import shutil
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

import tomli_w

from hugo_custom.utils.assets.constants import (
    CODE_EXTENSIONS,
    DEFAULT_ICON,
    EXT_ICONS,
    LOCK_ICONS,
)
from hugo_custom.utils.assets.og import make_og
from hugo_custom.utils.assets.vendors import (
    ensure_echarts,
    ensure_file_icons,
    ensure_fonts,
    ensure_katex,
    ensure_mermaid,
)
from hugo_custom.utils.dict import deep_merge
from hugo_custom.utils.fs import write_if_changed
from hugo_custom.utils.hugo import chroma_css
from hugo_custom.utils.paths import rel_of
from hugo_custom.utils.text import humanize, slugify

from .constants import CSS_MODULES, PACKAGE_DIR, TEMPLATES

if TYPE_CHECKING:
    from .builder import Builder


def icon_for(builder: Builder, src: Path) -> str | None:
    _ = builder
    ext = src.suffix.lower()
    if ext == ".md":
        return EXT_ICONS[".md"]
    if ext == ".ipynb":
        return EXT_ICONS[".ipynb"]
    if ext in CODE_EXTENSIONS:
        return LOCK_ICONS.get(src.name) or EXT_ICONS.get(ext, DEFAULT_ICON)
    return EXT_ICONS.get(ext, DEFAULT_ICON)


def css_bundle(builder: Builder) -> str:
    _ = builder
    src = TEMPLATES / "static" / "css" / "src"
    parts = []
    for name in CSS_MODULES:
        text = (src / f"{name}.css").read_text(encoding="utf-8").rstrip() + "\n"
        parts.append(text)
    return "\n".join(parts)


def tsc_cmd(builder: Builder) -> list[str] | None:
    _ = builder
    local = PACKAGE_DIR.parents[1] / "node_modules" / ".bin" / "tsc"
    if local.is_file():
        return [str(local)]
    if shutil.which("pnpm"):
        return ["pnpm", "dlx", "--package=typescript", "tsc"]
    if shutil.which("tsc"):
        return ["tsc"]
    return None


def stage_js(builder: Builder) -> None:
    site = builder.site
    out = site.stage / "static" / "js"
    if out.is_dir():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    cmd = tsc_cmd(builder)
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
        check=False,
    )
    if proc.returncode != 0:
        sys.exit(proc.stdout + proc.stderr)


def stage_assets(builder: Builder) -> None:
    site = builder.site
    stage = site.stage
    og_dir = stage / "static" / "og"
    og_dir.mkdir(parents=True, exist_ok=True)
    projects = sorted(
        {
            rel_of(site, p).split("/")[0]
            for p in builder.published
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
    mermaid = ensure_mermaid(site.vendor)
    if mermaid is not None:
        shutil.copytree(
            mermaid, stage / "static" / "vendor" / "mermaid", dirs_exist_ok=True
        )
    if site.params.get("graph", True):
        echarts = ensure_echarts(site.vendor)
        if echarts is not None:
            shutil.copytree(
                echarts,
                stage / "static" / "vendor" / "echarts",
                dirs_exist_ok=True,
            )
    shutil.rmtree(stage / "static" / "vendor" / "d3", ignore_errors=True)
    fonts = ensure_fonts(site.vendor)
    shutil.copytree(
        fonts, stage / "static" / "vendor" / "fonts", dirs_exist_ok=True
    )
    needed_icons = {
        icon for icon in (icon_for(builder, p) for p in builder.published) if icon
    }
    icons = ensure_file_icons(needed_icons, site.vendor)
    shutil.copytree(icons, stage / "static" / "icons", dirs_exist_ok=True)
    shutil.copytree(TEMPLATES / "layouts", stage / "layouts", dirs_exist_ok=True)
    dst = stage / "static" / "css"
    dst.mkdir(parents=True, exist_ok=True)
    write_if_changed(dst / "main.css", css_bundle(builder))
    stage_js(builder)
    write_if_changed(
        stage / "static" / "css" / "chroma.css",
        chroma_css("github", ':root:not([data-theme="dark"])')
        + "\n"
        + chroma_css("github-dark", ':root[data-theme="dark"]'),
    )


def stage_config(builder: Builder) -> None:
    site = builder.site
    cfg = tomllib.loads((TEMPLATES / "hugo.toml").read_text(encoding="utf-8"))
    cfg["title"] = site.title
    cfg["baseURL"] = site.site_url
    cfg["params"] = deep_merge(cfg.get("params") or {}, site.params)
    if site.homepage:
        cfg["params"]["homepage"] = site.homepage
    write_if_changed(site.stage / "hugo.toml", tomli_w.dumps(cfg))
