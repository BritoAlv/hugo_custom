# Work in progress

This page is in a folder listed in `.siteignore`, so it is **excluded on
deploy** (`HUGO_DEPLOY=true`) but visible in local previews.

Try it:

```sh
uv run hugo-custom                       # preview  -> this page is rendered
HUGO_DEPLOY=true uv run hugo-custom      # deploy   -> this page is missing
```