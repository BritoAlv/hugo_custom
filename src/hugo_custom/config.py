from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

CONFIG_FILENAME = "hugo_custom_site.toml"


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
    def load(cls, path: Path) -> SiteConfig:
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
