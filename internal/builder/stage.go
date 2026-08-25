package builder

import (
	"github.com/BritoAlv/hugo_custom/internal/config"
	"github.com/BritoAlv/hugo_custom/internal/discovery"
	"github.com/BritoAlv/hugo_custom/internal/utils"
)

type stageInput struct {
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
	siteConfig *config.SiteConfig,
	publishedSites *discovery.PublishedSet) (StageSummary, error) {
	panic("Not implemented still")
}
