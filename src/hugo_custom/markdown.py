from __future__ import annotations

import re

import yaml


def humanize(name: str) -> str:
    return " ".join(w[:1].upper() + w[1:] for w in re.split(r"[_\-]+", name))


def slugify(tag: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", tag.lower()).strip("-")


def extract_tags(text: str) -> list[str]:
    tags: list[str] = []
    lines = text.split("\n")
    i = 0
    keyword_re = re.compile(r"^#{2,4}\s*[Kk]eywords\.?\s*:?\s*$")
    while i < len(lines):
        if keyword_re.match(lines[i].strip()):
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            while (
                j < len(lines)
                and lines[j].strip()
                and not lines[j].lstrip().startswith("#")
            ):
                tag = re.sub(r"^\s*[-*]\s*", "", lines[j]).strip()
                tag = re.sub(r"[.,;:]+$", "", tag)
                if tag:
                    tags.append(tag)
                j += 1
            i = j
        else:
            i += 1
    return tags


def split_front_matter(text: str) -> tuple[dict | None, str]:
    if not text.startswith("---"):
        return None, text
    lines = text.split("\n", 2)
    if len(lines) < 3 or lines[1].strip() != "---":
        return None, text
    fm_text = lines[1]
    try:
        meta = yaml.safe_load(fm_text)
    except yaml.YAMLError:
        return None, text
    if not isinstance(meta, dict):
        return None, text
    rest = text[len("---\n") + len(fm_text) + len("\n---\n") :]
    return meta, rest


def front_matter(meta: dict) -> str:
    dump = yaml.safe_dump(
        meta, sort_keys=False, allow_unicode=True, default_flow_style=False
    ).rstrip()
    return f"---\n{dump}\n---\n\n"


def split_title(body: str) -> tuple[str | None, str]:
    """Return the first heading (any level, like Quarto's title rule) and the
    body without it. A leading front-matter block is skipped."""
    lines = body.split("\n")
    start = 0
    if lines and lines[0].strip() == "---":
        start = 1
        while start < len(lines) and lines[start].strip() != "---":
            start += 1
        start += 1
    for i in range(start, len(lines)):
        m = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", lines[i])
        if m and m.group(1).strip():
            return m.group(1).strip(), "\n".join(lines[:i] + lines[i + 1 :])
    return None, body


def ipynb_to_markdown(nb: dict) -> str:
    """Convert notebook cells to markdown without executing anything:
    markdown cells pass through, code cells become fenced blocks and stored
    text/image outputs are kept as-is."""
    lang = (nb.get("metadata") or {}).get("kernelspec", {}).get("language", "python")
    out: list[str] = []
    for cell in nb.get("cells", []):
        ctype = cell.get("cell_type")
        source = "".join(cell.get("source", []))
        if ctype == "markdown":
            out.append(source)
            out.append("")
        elif ctype == "code":
            code = source.rstrip()
            if code:
                run = max((len(m) for m in re.findall(r"`+", code)), default=0)
                fence = "`" * max(3, run + 1)
                out.append(f"{fence}{lang}")
                out.append(code)
                out.append(fence)
                out.append("")
            for output in cell.get("outputs", []):
                otype = output.get("output_type")
                if otype in ("stream", "execute_result", "display_data"):
                    if otype == "stream":
                        text = "".join(output.get("text", []))
                    else:
                        data = output.get("data") or {}
                        text = "".join(data.get("text/plain") or [])
                    if text and text.strip():
                        out.append("```")
                        out.append(text.rstrip())
                        out.append("```")
                        out.append("")
                    data = output.get("data") or {}
                    for mime, payload in data.items():
                        if mime.startswith("image/") and isinstance(payload, str):
                            out.append(f"![]({mime}:base64,{payload})")
                            out.append("")
    return "\n".join(out)
