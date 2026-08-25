package main

import (
	"flag"
	"os"

	"github.com/BritoAlv/hugo_custom/internal/builder"
	"github.com/BritoAlv/hugo_custom/internal/builder/plugins"
	"github.com/BritoAlv/hugo_custom/internal/config"
	"github.com/BritoAlv/hugo_custom/internal/discovery"
	"github.com/BritoAlv/hugo_custom/internal/render"
	"github.com/charmbracelet/log"
)

func main() {
	var root string
	flag.StringVar(
		&root,
		"root",
		"",
		"Path to Project Root:  hugo_custom_site.toml file should be inside")
	flag.Parse()
	logger := log.New(os.Stderr)

	if root == "" {
		logger.Error("missing required --root argument")
		os.Exit(1)
	}

	logger.Info("build: — resolving repo root", "root", root)

	siteConfig, err := config.Load(root)

	if err != nil {
		logger.Error("build: failed to load configuration", "err", err)
		os.Exit(1)
	}

	logger.Info("build: — configuration loaded correctly")

	publishedSet, err := discovery.Discover(root, true)
	if err != nil {
		logger.Error("build: failed file discovery process", "err", err)
	}
	logger.Info("build: — files discovered correctly")

	_, err = builder.Stage(
		siteConfig,
		publishedSet,
		[]builder.FilePluginInterface{plugins.MarkdownPlugin{}},
		[]builder.EnricherPluginInterface{plugins.AssetsEnricherPlugin{}})

	if err != nil {
		logger.Error("build: failed the staging process", "err", err)
	}

	err = render.Render(render.Input{
		ProjectRoot: root,
		StageDir:    siteConfig.LocationConfig.StageDir,
		OutputDir:   siteConfig.LocationConfig.OutputDir,
	})

	if err != nil {
		logger.Error("build: failed rendering the staged site", "err", err)
	}
}