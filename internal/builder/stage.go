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

type stageState struct {
}

type StageSummary struct {
	Pages        int
	Nodes        int
	ContentFiles int
	StaticFiles  int
}

func Stage(
	siteConfig *config.SiteConfig,
	publishedSites *discovery.PublishedSet) (StageSummary, error) {
	panic("Not implemented still")
}
