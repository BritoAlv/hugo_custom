from __future__ import annotations

import re


def humanize(name: str) -> str:
    return " ".join(w[:1].upper() + w[1:] for w in re.split(r"[_\-]+", name))


def slugify(tag: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", tag.lower()).strip("-")
