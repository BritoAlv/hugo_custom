from __future__ import annotations

import subprocess


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
