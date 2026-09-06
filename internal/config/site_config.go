package config

import (
	"fmt"
	"path/filepath"

	"github.com/BritoAlv/hugo_custom/internal/utils"
	"github.com/BurntSushi/toml"
)

const ConfigFileName = "hugo_custom_site.toml"

type LocationConfig struct {
	ProjectRoot   utils.Path
	ContentSource utils.Path
	StageDir      utils.Path
	OutputDir     utils.Path
	CacheDir      utils.Path
}

type SiteMeta struct {
	Title            string
	SiteURL          string
	HomePageMarkdown utils.Path
}

type SiteConfig struct {
	LocationConfig LocationConfig
	SiteMeta       SiteMeta
}

type tomlConfig struct {
	Source   string `toml:"source"`
	HomePage string `toml:"homepage"`
	Siteurl  string `toml:"site-url"`
	Title    string `toml:"title"`
}

func Load(root utils.Path) (*SiteConfig, error) {
	projectRoot, err := filepath.Abs(root)
	if err != nil {
		return nil, fmt.Errorf("config: resolving root %q: %w", root, err)
	}
	var raw tomlConfig
	_, err = toml.DecodeFile(filepath.Join(projectRoot, ConfigFileName), &raw)
	if err != nil {
		return nil, fmt.Errorf("config: decoding %s : %w", ConfigFileName, err)
	}

	return &SiteConfig{
		LocationConfig: LocationConfig{
			ProjectRoot:   projectRoot,
			ContentSource: filepath.Join(projectRoot, raw.Source),
			StageDir:      filepath.Join(projectRoot, "hugo_src_go"),
			OutputDir:     filepath.Join(projectRoot, "site_go"),
			CacheDir:      utils.CacheDir(),
		},
		SiteMeta: SiteMeta{
			Title:            raw.Title,
			SiteURL:          raw.Siteurl,
			HomePageMarkdown: raw.HomePage,
		},
	}, nil
}
