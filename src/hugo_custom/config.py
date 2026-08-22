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
    homepage: str | None
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
        title = str(data.get("title", root.name))
        brand_raw = data.get("brand")
        if brand_raw is None:
            brand = title.upper().replace("_", " ")
        else:
            brand = str(brand_raw)
        source_raw = data.get("source", ".")
        if source_raw == "self":
            import sys

            print(
                "warning: source = \"self\" is deprecated, use source = \".\" "
                "(repo root) instead",
                file=sys.stderr,
            )
            source_raw = "."
        return cls(
            root=root,
            source=root / source_raw,
            stage=root / data.get("stage", "hugo_src"),
            output=root / data.get("output", "site"),
            siteignore=(root / siteignore) if siteignore else None,
            ignore=ignore,
            title=title,
            site_url=str(data.get("site-url", "")),
            brand=brand,
            homepage=(
                str(data["homepage"]).strip().lstrip("./")
                if "homepage" in data
                else None
            ),
            cache_dir=cache_dir,
            params=dict(data.get("params", {})),
        )



