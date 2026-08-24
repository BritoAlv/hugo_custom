package main

import (
	"flag"
	"fmt"
	"os"
	"github.com/BritoAlv/hugo_custom/internal/config"
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
	fmt.Println(siteConfig.SiteMeta.Title)
}
