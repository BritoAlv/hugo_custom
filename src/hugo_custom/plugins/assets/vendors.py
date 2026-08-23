from __future__ import annotations

import io
import os
import re
import shutil
import sys
import tarfile
import urllib.request
from pathlib import Path

from hugo_custom.plugins.assets.constants import (
    ECHARTS_URLS,
    ECHARTS_VERSION,
    GOOGLE_FONTS_URL,
    GSTATIC_RE,
    ICON_ALT,
    ICON_BASE,
    KATEX_TARBALL,
    KATEX_VERSION,
    MERMAID_URLS,
    MERMAID_VERSION,
    USER_AGENT,
)
from hugo_custom.utils.extensions import DEFAULT_ICON


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
                rel = member.name[len("package/dist/") :]
                if rel in ("katex.min.js", "katex.min.css") or rel.startswith(
                    ("fonts/", "contrib/")
                ):
                    member.name = rel
                    tar.extract(member, tmp, filter="data")
    except (OSError, tarfile.TarError) as exc:
        shutil.rmtree(tmp, ignore_errors=True)
        sys.exit(
            f"KaTeX assets are not cached in {cache} and fetching {KATEX_TARBALL} "
            f"failed: {exc}"
        )
    shutil.rmtree(cache, ignore_errors=True)
    os.replace(tmp, cache)
    print(f"fetched KaTeX {KATEX_VERSION} into {cache}")
    return cache


def ensure_mermaid(vendor: Path) -> Path | None:
    """Return a directory with the pinned Mermaid UMD bundle, downloading and
    caching if needed. Returns None when the bundle cannot be fetched — the
    site still builds, diagrams just stay unrendered."""
    cache = vendor / "mermaid"
    marker = cache / "version.txt"
    if (
        (cache / "mermaid.min.js").is_file()
        and marker.is_file()
        and marker.read_text(encoding="utf-8").strip() == MERMAID_VERSION
    ):
        return cache
    tmp = cache.with_suffix(".tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    data = None
    last_exc: Exception | None = None
    for url in MERMAID_URLS:
        try:
            with urllib.request.urlopen(url, timeout=120) as resp:
                data = resp.read()
            break
        except OSError as exc:
            last_exc = exc
    if data is None or not data.strip():
        shutil.rmtree(tmp, ignore_errors=True)
        print(
            f"warning: Mermaid assets are not cached in {cache} and fetching "
            f"from {', '.join(MERMAID_URLS)} failed: {last_exc}",
            file=sys.stderr,
        )
        return None
    (tmp / "mermaid.min.js").write_bytes(data)
    (tmp / "version.txt").write_text(MERMAID_VERSION, encoding="utf-8")
    shutil.rmtree(cache, ignore_errors=True)
    os.replace(tmp, cache)
    print(f"fetched Mermaid {MERMAID_VERSION} into {cache}")
    return cache


def ensure_echarts(vendor: Path) -> Path | None:
    """Return a directory with the pinned ECharts UMD bundle, downloading and
    caching if needed. Returns None when the bundle cannot be fetched — the
    site still builds, the graph page just stays unrendered."""
    cache = vendor / "echarts"
    marker = cache / "version.txt"
    if (
        (cache / "echarts.min.js").is_file()
        and marker.is_file()
        and marker.read_text(encoding="utf-8").strip() == ECHARTS_VERSION
    ):
        return cache
    tmp = cache.with_suffix(".tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    data = None
    last_exc: Exception | None = None
    for url in ECHARTS_URLS:
        try:
            with urllib.request.urlopen(url, timeout=120) as resp:
                data = resp.read()
            break
        except OSError as exc:
            last_exc = exc
    if data is None or not data.strip():
        shutil.rmtree(tmp, ignore_errors=True)
        print(
            f"warning: ECharts assets are not cached in {cache} and fetching "
            f"from {', '.join(ECHARTS_URLS)} failed: {last_exc}",
            file=sys.stderr,
        )
        return None
    (tmp / "echarts.min.js").write_bytes(data)
    (tmp / "version.txt").write_text(ECHARTS_VERSION, encoding="utf-8")
    shutil.rmtree(cache, ignore_errors=True)
    os.replace(tmp, cache)
    print(f"fetched ECharts {ECHARTS_VERSION} into {cache}")
    return cache


def ensure_fonts(vendor: Path) -> Path:
    """Return a directory with Lato woff2 + a local @font-face stylesheet, cached on disk."""
    cache = vendor / "fonts"
    if (cache / "lato.css").is_file() and any((cache / "lato").glob("*.woff2")):
        return cache
    tmp = cache.with_suffix(".tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    (tmp / "lato").mkdir(parents=True)

    def fetch(url: str) -> bytes:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.read()

    try:
        css = fetch(GOOGLE_FONTS_URL).decode()
    except OSError as exc:
        shutil.rmtree(tmp, ignore_errors=True)
        sys.exit(
            f"Lato fonts are not cached in {cache} and fetching {GOOGLE_FONTS_URL} failed: {exc}"
        )

    def localize(match: re.Match) -> str:
        url = match.group(1)
        name = url.rsplit("/", 1)[-1].split("?")[0]
        dest = tmp / "lato" / name
        if not dest.is_file():
            try:
                dest.write_bytes(fetch(url))
            except OSError as exc:
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
    the vscode-icons set (with `ICON_ALT` fallbacks; cached on disk; failed
    fetches fall back to the generic file icon)."""
    cache = vendor / "icons"
    cache.mkdir(parents=True, exist_ok=True)
    wanted = names | {DEFAULT_ICON}
    fetched = {p.name.removesuffix(".svg") for p in cache.glob("*.svg")}
    missing = wanted - fetched
    if not missing:
        return cache

    def fetch(url: str) -> str | None:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
        except OSError:
            return None
        if resp.status != 200 or not data.strip():
            return None
        return data.decode("utf-8")

    for name in sorted(missing):
        data = fetch(ICON_BASE + name + ".svg")
        if data is None and name in ICON_ALT:
            data = fetch(ICON_ALT[name])
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
