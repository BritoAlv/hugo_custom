from __future__ import annotations

import posixpath
import re

FENCE_RE = re.compile(r"^\s*(```|~~~)")
LINK_RE = re.compile(r"\]\(([^)]+)\)")


def extract_refs(body: str, base_dir: str) -> set[str]:
    """Collect internal reference destinations (raw rel paths, normalized)
    from markdown `body`, resolved from `base_dir`. Skips fenced code blocks
    and external/absolute/anchor destinations, mirroring `rebase_links` and
    the render-link.html hook's scope. Fragment/query suffixes are dropped."""
    refs: set[str] = set()
    out = []
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
            out.append(line)
    for line in out:
        for match in LINK_RE.finditer(line):
            dest = match.group(1).strip()
            if dest[0:1] in ("#", "/") or dest.startswith(
                ("http://", "https://", "mailto:", "data:")
            ):
                continue
            head = re.split(r"[#?]", dest, 1)[0].strip()
            if not head:
                continue
            rel = posixpath.normpath(posixpath.join(base_dir or ".", head))
            if rel in ("", ".", "..") or rel.startswith("../"):
                continue
            refs.add(rel)
    return refs


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
