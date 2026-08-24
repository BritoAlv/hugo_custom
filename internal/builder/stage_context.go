package builder

import (
	"github.com/BritoAlv/hugo_custom/internal/config"
	"github.com/BritoAlv/hugo_custom/internal/discovery"
)

type StageContext struct {
	SiteConfig config.SiteConfig
	Published  discovery.PublishedSet
}

func NewStageContext(site config.SiteConfig, published discovery.PublishedSet) *StageContext {
	return &StageContext{
		SiteConfig: site,
		Published:  published,
	}
}
