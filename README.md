# Hugo Custom

## What Problem This Solves?

Let's say you have a folder with your notes, *.md*, code, etc, and you would like to put all of that in a website where references across the content work, and it can be deployed, so anyone can read it. A tool like Hugo does precisely this, but to add features or customization, something extra is needed.

## What It Is?

A generic Hugo pipeline that turns **a folder of Markdown, notebooks and code** into a fully self-contained static website: staged Hugo project,
rendered site, vendored KaTeX, local fonts, per-extension file icons, tags
page, per-project OG images, search and code views for every source file.

The tooling is a Python package (`hugo-custom`) installed and run through
`uv`. A content repo only needs a `hugo_custom_site.toml` — no Hugo
configuration is developed inside the content repo; the pipeline generates a
complete Hugo project (content, layouts, static assets, `hugo.toml`) in the
`stage` directory and renders it with Hugo.

## Requirements

- [uv](https://docs.astral.sh/uv/)
- [Hugo](https://gohugo.io/installation/) (extended edition, 0.165+)
- git

## Quick start

### 1. Add `hugo_custom_site.toml` to your repo root

The tool locates this file automatically by walking up from the current
directory, so it must sit at the top of the repo:

```toml
title = "My Articles"
site-url = "https://yourname.github.io/myarticles/"
source = "self"           # folder with the content
stage = "hugo_src"        # generated Hugo project (add to .gitignore)
output = "site"           # rendered site (add to .gitignore)
# brand = "MY ARTICLES"   # text on the OG images (default: TITLE uppercased)
# siteignore = ".siteignore"  # optional, see "Deploy-only exclusions"
```

The site title/URL and every visual or behavior option live here. See
[Configuration](#configuration) for the full reference, and
`examples/hugo_custom_site.toml` for a commented template.

### 2. Ignore the generated output

Add this to the repo `.gitignore` — the stage and output dirs are fully
regenerated on every build:

```gitignore
# hugo-custom generated output
/hugo_src/     # staged Hugo project (the `stage` dir)
/site/         # rendered site (the `output` dir)
```

Use the actual `stage`/`output` values from `hugo_custom_site.toml` if you
changed them. Keep `hugo_custom_site.toml` and `siteignore` committed —
they are configuration. Since the pipeline uses this `.gitignore` to decide
what gets published from `source/`, these entries double as build-noise
exclusions.

### 3. Preview locally

```bash
cd /path/to/content-repo
uvx --from /path/to/hugo_custom hugo-custom --preview
# or from GitHub:
# uvx --from git+https://github.com/BritoAlv/hugo_custom.git@main hugo-custom --preview
```

This stages the site and starts Hugo's dev server with hot reload
(Ctrl-C to stop). Open the printed URL.

### 4. Build for production locally

```bash
cd /path/to/content-repo
uvx --from /path/to/hugo_custom hugo-custom --deploy
# or from GitHub:
# uvx --from git+https://github.com/BritoAlv/hugo_custom.git@main hugo-custom --deploy
```

Deploy mode is stricter: it applies `.siteignore` exclusions.

### Offline use

Everything works without network after an initial warm-up run:

- The `uvx --from /path/to/hugo_custom` build itself never touches the
  network (only `--from git+...` does).
- Vendored assets (KaTeX, Lato fonts, file icons) are downloaded on first
  build and cached in `~/.cache/hugo_custom` (see
  [Caching](#caching)); later builds reuse the cache.
- `uv` caches the package build too, so the second run is fully offline.

### 5. Deploy on GitHub Pages

1. In your repo: **Settings → Pages → Source: GitHub Actions**.
2. Add `.github/workflows/deploy.yml` to your content repo:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  deploy:
    uses: BritoAlv/hugo_custom/.github/workflows/deploy-pages.yml@main
    # config: hugo_custom_site.toml   # only needed if renamed/moved
```

3. Push. The reusable workflow installs Hugo + uv, runs the deploy build via
   `uvx`, and uploads `site/` to Pages.

## Configuration

`hugo_custom_site.toml` — all keys optional unless noted:

| Key | Default | Meaning |
|---|---|---|
| `title` | repo directory name | Site title (used in the navbar, `<title>`, index page) |
| `site-url` | `""` | Canonical URL, required for OG images to be absolute |
| `brand` | `title` uppercased | Text drawn on the generated OG images |
| `source` | `self` | Folder with the content (relative to repo root; `.` = the repo itself) |
| `stage` | `hugo_src` | Generated Hugo project (add to `.gitignore`) |
| `output` | `site` | Rendered site (add to `.gitignore`) |
| `siteignore` | none | Path to a deploy-only ignore file (see below) |
| `ignore` | `[]` | Always-applied exclusion patterns (gitignore syntax) |
| `cache-dir` | `$XDG_CACHE_HOME/hugo_custom` | Where vendored assets are cached |
| `[params]` | none | Extra keys merged into the Hugo `params` section |

The built-in template (`src/hugo_custom/templates/hugo.toml`) provides the
baseline: pretty URLs, tags taxonomy, search index (`/index.json`), KaTeX
math via the goldmark passthrough extension, Chroma syntax highlighting and
the light/dark CSS theme.

Example overrides:

```toml
[params]
description = "My site"
```

`cache-dir` also honors the `HUGO_CUSTOM_CACHE` environment variable.

## Content conventions

The pipeline treats the folder tree under `source/` as the site structure:

- **Markdown** (`.md`): rendered as pages. `## Keywords` (or `### Keywords:`)
  sections are parsed into tags, which feed the tags pages, sidebar and
  `.page-meta` block. Dates are taken from git history (`date` from the
  first commit, `lastmod` from the last). Front matter is preserved and
  enriched; the first H1 becomes the page title.
- **Jupyter notebooks** (`.ipynb`): converted to static Markdown pages —
  markdown cells pass through, code cells become highlighted blocks and the
  stored outputs (text/images) are kept as-is. Notebooks are **not**
  executed.
- **Code files** (`.rs`, `.py`, `.toml`, `.sh`, `.js`, …): a `codeview/`
  page is generated for each, showing the file with syntax highlighting and a
  download link; markdown links to code files are rewritten to point at their
  codeview page.
- **Other files** (images, data, PDFs…): copied verbatim and served as-is.

Exclusions:

- Files ignored by your repo's `.gitignore` (root and nested) are never
  published.
- The `ignore` key in `hugo_custom_site.toml` adds always-applied patterns
  (gitignore syntax, relative to the repo root), e.g.
  `ignore = [".github/", "docs/secret/"]`.
- A `siteignore` file lists paths excluded **only on deploy** — useful for
  marking content "not ready yet" while keeping it in the repo and in local
  previews:

  ```
  source/wip_project/
  source/rough_draft.md
  ```

  (Use paths relative to the repo root, e.g. `self/async_rust/`.)

## Testing (this repo)

This repository is its own test bed: it publishes itself to
[britoalv.github.io/hugo_custom/](https://britoalv.github.io/hugo_custom/).

- `hugo_custom_site.toml` sets `source = "."` — the pipeline builds a site
  from the repo's own files, exercising code views, file icons, OG images,
  the sidebar tree and generated pages.
- `ignore` excludes what the pipeline would not render as pages anyway:
  `.github/` (dot-directories), the root `README.md`, `examples/` and
  `src/hugo_custom/templates/` (the layouts/config that are copied into the
  staged project). Excluding them keeps the sidebar free of dead links.
- `.github/workflows/deploy.yml` deploys to Pages using the reusable workflow
  with `package: .`, so the deployed site is built from the exact commit that
  triggered it (dogfooding).

## What the pipeline does

1. **Collect** — walk `source/`, apply ignore specs (`.gitignore` +
   nested + `siteignore` on deploy).
2. **Stage** — build `stage/` (`hugo_src/`): processed markdown and
   notebook pages in `content/`, `codeview/` pages, raw files in `static/`,
   generated `data/sidebar.yml` (the sidebar tree), `hugo.toml` and the
   layout/asset templates.
3. **Render** — `hugo --source hugo_src --destination site`.
4. **Vendor** — pinned KaTeX and Lato fonts and the file icons are copied
   into `static/vendor/` and `static/icons/` during staging, so the built
   site is fully self-contained (no CDN references).

Vendored assets (KaTeX tarball, Google Fonts woff2, vscode-icons SVGs) are
downloaded on first use and cached, so builds are fast and work offline after
the first run.

## Caching

Vendored assets live in `$XDG_CACHE_HOME/hugo_custom` (default
`~/.cache/hugo_custom`), overridable per site with `cache-dir` in
`hugo_custom_site.toml` or globally with the `HUGO_CUSTOM_CACHE`
environment variable.
To share a warm cache across machines (CI, new laptop), copy that directory
or point both at a shared location.

## Development

Iterate locally with `uv run` — it always rebuilds from the current source
(`uvx --from .` caches by name+version, so after code changes it needs a
version bump or `uv cache clean`):

```bash
uv sync
uv run hugo-custom --help
uv run hugo-custom          # build this repo's own site from its files
```

Test against any content repo without installing anything:

```bash
uv run hugo-custom --config /path/to/content/hugo_custom_site.toml --preview
```

And use a `file:` dependency
(`uv add hugo-custom@file:///path/to/hugo_custom`) if you prefer a
lockfile-based workflow in the content repo.