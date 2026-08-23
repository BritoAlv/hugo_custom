from __future__ import annotations

import shutil
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

import tomli_w

from hugo_custom.plugins.assets.bundle import css_bundle, icon_for_path, tsc_cmd
from hugo_custom.plugins.assets.og import make_og
from hugo_custom.plugins.assets.vendors import (
    ensure_echarts,
    ensure_file_icons,
    ensure_fonts,
    ensure_katex,
    ensure_mermaid,
)
from hugo_custom.plugins.base import Plugin
from hugo_custom.utils.fs import write_if_changed
from hugo_custom.utils.hugo import chroma_css
from hugo_custom.utils.paths import templates_dir
from hugo_custom.utils.text import humanize, slugify

if TYPE_CHECKING:
    from hugo_custom.builder.context import StageContext


class AssetsPlugin(Plugin):
    name = "assets"

    def post_stage(self, ctx: StageContext) -> None:
        site = ctx.site
        stage = site.stage

        # --- OG images ---
        og_dir = stage / "static" / "og"
        og_dir.mkdir(parents=True, exist_ok=True)
        projects = sorted(
            {
                ctx.rel_of(p).split("/")[0]
                for p in ctx.published
                if "/" in ctx.rel_of(p)
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

        # --- vendor assets ---
        katex = ensure_katex(site.vendor)
        shutil.copytree(katex, stage / "static" / "vendor" / "katex", dirs_exist_ok=True)
        mermaid = ensure_mermaid(site.vendor)
        if mermaid is not None:
            shutil.copytree(mermaid, stage / "static" / "vendor" / "mermaid", dirs_exist_ok=True)
        if site.params.get("graph", True):
            echarts = ensure_echarts(site.vendor)
            if echarts is not None:
                shutil.copytree(
                    echarts, stage / "static" / "vendor" / "echarts", dirs_exist_ok=True
                )
        shutil.rmtree(stage / "static" / "vendor" / "d3", ignore_errors=True)
        fonts = ensure_fonts(site.vendor)
        shutil.copytree(fonts, stage / "static" / "vendor" / "fonts", dirs_exist_ok=True)

        needed_icons = {
            icon for icon in (icon_for_path(p) for p in ctx.published) if icon
        }
        icons = ensure_file_icons(needed_icons, site.vendor)
        shutil.copytree(icons, stage / "static" / "icons", dirs_exist_ok=True)

        shutil.copytree(templates_dir() / "layouts", stage / "layouts", dirs_exist_ok=True)

        dst = stage / "static" / "css"
        dst.mkdir(parents=True, exist_ok=True)
        write_if_changed(dst / "main.css", css_bundle())
        self._stage_js(ctx)
        write_if_changed(
            stage / "static" / "css" / "chroma.css",
            chroma_css("github", ':root:not([data-theme="dark"])')
            + "\n"
            + chroma_css("github-dark", ':root[data-theme="dark"]'),
        )

        # --- hugo config ---
        self._stage_config(ctx)

    def _stage_js(self, ctx: StageContext) -> None:
        site = ctx.site
        out = site.stage / "static" / "js"
        if out.is_dir():
            shutil.rmtree(out)
        out.mkdir(parents=True)
        cmd = tsc_cmd()
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
                str(templates_dir() / "static" / "ts" / "tsconfig.json"),
                "--outDir",
                str(out),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            sys.exit(proc.stdout + proc.stderr)

    def _stage_config(self, ctx: StageContext) -> None:
        from hugo_custom.plugins.assets.constants import deep_merge

        site = ctx.site
        cfg = tomllib.loads((templates_dir() / "hugo.toml").read_text(encoding="utf-8"))
        cfg["title"] = site.title
        cfg["baseURL"] = site.site_url
        cfg["params"] = deep_merge(cfg.get("params") or {}, site.params)
        if site.homepage:
            cfg["params"]["homepage"] = site.homepage
        write_if_changed(site.stage / "hugo.toml", tomli_w.dumps(cfg))
