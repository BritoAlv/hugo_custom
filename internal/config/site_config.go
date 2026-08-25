package config

import "github.com/BritoAlv/hugo_custom/internal/utils"


const ConfigFileName = "hugo_custom_site.toml"

type LocationConfig struct {
	ProjectRoot utils.Path
	ContentSource utils.Path
	StageDir utils.Path
	OutputDir utils.Path
	CacheDir utils.Path
}

type SiteMeta struct {
	Title string
	SiteURL string
	HomePageMarkdown utils.Path
}


type SiteConfig struct {
	LocationConfig LocationConfig
	SiteMeta SiteMeta
}

func Load( root utils.Path ) (*SiteConfig, error) {
	panic("Not Implemented")
}