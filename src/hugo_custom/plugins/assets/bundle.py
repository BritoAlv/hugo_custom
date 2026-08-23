from __future__ import annotations

import shutil
from pathlib import Path

from hugo_custom.utils.paths import package_dir, templates_dir

from .constants import CSS_MODULES


def icon_for_path(path: Path) -> str | None:
    from hugo_custom.utils.extensions import CODE_EXTENSIONS, DEFAULT_ICON, EXT_ICONS, LOCK_ICONS

    ext = path.suffix.lower()
    if ext == ".md":
        return EXT_ICONS[".md"]
    if ext == ".ipynb":
        return EXT_ICONS[".ipynb"]
    if ext in CODE_EXTENSIONS:
        return LOCK_ICONS.get(path.name) or EXT_ICONS.get(ext, DEFAULT_ICON)
    return EXT_ICONS.get(ext, DEFAULT_ICON)


def css_bundle() -> str:
    src = templates_dir() / "static" / "css" / "src"
    parts = []
    for name in CSS_MODULES:
        text = (src / f"{name}.css").read_text(encoding="utf-8").rstrip() + "\n"
        parts.append(text)
    return "\n".join(parts)


def tsc_cmd() -> list[str] | None:
    local = package_dir().parents[1] / "node_modules" / ".bin" / "tsc"
    if local.is_file():
        return [str(local)]
    if shutil.which("pnpm"):
        return ["pnpm", "dlx", "--package=typescript", "tsc"]
    if shutil.which("tsc"):
        return ["tsc"]
    return None
