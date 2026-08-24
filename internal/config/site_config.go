package config

type Path = string

const configFileName = "hugo_custom_site.toml"

type LocationConfig struct {
	ProjectRoot Path
	ContentSource Path
	StageDir Path
	OutputDir Path
	CacheDir Path
}

type SiteMeta struct {
	Title string
	SiteURL string
	HomePageMarkdown Path
}


type SiteConfig struct {
	LocationConfig LocationConfig
	SiteMeta SiteMeta
}

func Load( root Path ) (*SiteConfig, error) {
	panic("Not Implemented")
}