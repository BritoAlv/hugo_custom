package builder

import (
	"github.com/BritoAlv/hugo_custom/internal/config"
	"github.com/BritoAlv/hugo_custom/internal/utils"
)

type pluginContext struct {
	SiteConfig *config.SiteConfig
	Published  []utils.Path
}

type StageSummary struct {
	Nodes        int
	ContentFiles int
	StaticFiles  int
}

type sourceEntry struct {
	SourceRelativePath string
	Label              string
	Kind               string
	Body               string
}

func Stage(
	siteConfig *config.SiteConfig, published []utils.Path) (StageSummary, error) {
	panic("Not implemented still")
}
