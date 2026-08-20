---
tags: [overview, references]
---

# Overview

This is the example site for **references between files**. Every section below
shows one type of reference and links to a real target, so you can click
around and inspect the rendered HTML to see how each link was rewritten.

The source of each link is a plain markdown link whose **text matches the path
you write**, and the path is **relative to this file's folder** (`notes/`).

<!--
  What you see in the rendered page: the template
  src/hugo_custom/templates/layouts/_default/_markup/render-link.html rewrites
  every markdown link at build time. Rules:

  - .md / .ipynb links      -> rewritten to the target page's permalink
  - code-file links         -> rewritten to the target's codeview page
  - other files (assets)    -> left as written; the browser resolves them
                               relative to the page URL (depth matters!)
  - http(s)://, mailto:,    -> left untouched
    #anchor and /absolute
-->

## Markdown to markdown, same folder

[setup.md](setup.md)

## Markdown to markdown, subfolder

[deep/subpage.md](deep/subpage.md)

## Markdown to markdown, with anchor

Links to a section of another page; the `#requirements` anchor is preserved:

[setup.md#requirements](setup.md#requirements)

## Markdown to notebook

The notebook is converted to a static page; the link points at it:

[../notebooks/analysis.ipynb](../notebooks/analysis.ipynb)

## Markdown to code file

Code files get a `codeview/` page (syntax highlighting + download link); the
link is rewritten to point at it:

[../code/main.py](../code/main.py)

## Markdown to static assets

Other files (images, data, PDFs, videos) are copied verbatim to the site root
and served as-is. Their links point at a `preview/` page that embeds the file
inline (with a download link), so write the path relative to this file's
folder: from `notes/`, one level up reaches `references/assets/`:

[../assets/diagram.svg](../assets/diagram.svg)

[../assets/sample.csv](../assets/sample.csv)

[../assets/sample.mp4](../assets/sample.mp4)

## External links

Absolute URLs pass through unchanged (and get `rel="noopener"`):

[https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)
