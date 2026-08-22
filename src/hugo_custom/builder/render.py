from __future__ import annotations

import shutil
import subprocess
import sys
from typing import TYPE_CHECKING

from hugo_custom.utils.network import lan_ip
from hugo_custom.utils.text import slugify

from .constants import CODE_OUTPUT_DIR

if TYPE_CHECKING:
    from .builder import Builder


def render(builder: Builder) -> None:
    site = builder.site
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


def preview(builder: Builder, host: str = "127.0.0.1") -> None:
    site = builder.site
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


def summary(builder: Builder) -> None:
    site = builder.site
    n_pages = len(list(site.output.rglob("*.html")))
    n_code = sum(1 for rel, _, _ in builder.pages if rel.startswith(CODE_OUTPUT_DIR))
    n_md = sum(1 for rel, _, _ in builder.pages if rel.endswith(".md"))
    n_tags = len({slugify(t) for _, tags, _ in builder.pages for t in tags})
    print(
        f"rendered {n_pages} pages ({n_md} markdown, {n_code} code views), {n_tags} tags"
    )
