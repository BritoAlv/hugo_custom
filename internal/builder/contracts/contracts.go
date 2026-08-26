package contracts

import (
	"github.com/BritoAlv/hugo_custom/internal/config"
	"github.com/BritoAlv/hugo_custom/internal/utils"
)

type FilePluginInterface interface {
	Name() string
	Handles(src utils.Path) bool
	Process(input PluginContext, src utils.Path) (*SourceEntry, error)
}

type EnricherPluginInterface interface {
	Name() string
	Enrich(input PluginContext, sources []SourceEntry) error
}

type PluginContext struct {
	SiteConfig *config.SiteConfig
	Published  []utils.Path
}

type SourceEntry struct {
	SourceRelativePath string
	Label              string
	Kind               string
	Body               string
}