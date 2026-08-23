from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


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


def run_hugo(stage: Path, output: Path, root: Path) -> None:
    if output.exists():
        shutil.rmtree(output)
    result = subprocess.run(
        ["hugo", "--source", str(stage), "--destination", str(output)],
        cwd=root,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        sys.exit(f"hugo build failed with exit code {result.returncode}")


def serve_hugo(stage: Path, output: Path, root: Path, host: str = "127.0.0.1") -> None:
    from hugo_custom.utils.network import lan_ip

    cmd = [
        "hugo",
        "server",
        "--source",
        str(stage),
        "--destination",
        str(output),
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
    subprocess.run(cmd, cwd=root, check=False)
