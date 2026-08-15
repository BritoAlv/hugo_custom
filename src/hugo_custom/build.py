from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from hugo_custom.builder import Builder
from hugo_custom.config import CONFIG_FILENAME, SiteConfig, find_config

DEPLOY_ENV = "HUGO_DEPLOY"


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Stage a content folder into a Hugo site project, build it and "
            "vendor runtime assets (KaTeX, fonts, icons)."
        )
    )
    parser.add_argument(
        "-c",
        "--config",
        default=None,
        help=(
            f"path to the {CONFIG_FILENAME} configuration (default: "
            f"{CONFIG_FILENAME} at the top of the repo, found by walking up "
            "from the current directory)"
        ),
    )
    parser.add_argument(
        "--deploy", action="store_true", help="apply .siteignore exclusions"
    )
    parser.add_argument(
        "--stage-only",
        action="store_true",
        help="build the staged hugo project without rendering",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="stage then run hugo server on the staged project",
    )
    args = parser.parse_args()

    config_path = Path(args.config) if args.config else find_config(Path.cwd())
    if config_path is None:
        sys.exit(f"no {CONFIG_FILENAME} found in {Path.cwd()} or any parent directory")
    deploy = args.deploy or os.environ.get(DEPLOY_ENV, "").lower() == "true"

    site = SiteConfig.load(config_path)
    builder = Builder(site, deploy, preview_mode=args.preview)
    builder.stage()
    print(
        f"staged {len(builder.published)} published files from {site.source} into {site.stage}"
    )
    if args.stage_only:
        return
    if args.preview:
        builder.preview()
    else:
        builder.render()
        builder.summary()


if __name__ == "__main__":
    main()
