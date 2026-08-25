package plugins

import "github.com/BritoAlv/hugo_custom/internal/builder"

type AssetsEnricherPlugin struct{}

func (AssetsEnricherPlugin) Name() string {
	return "Assets Enricher Plugin"
}

func (AssetsEnricherPlugin) Enrich(input builder.StageInput, state *builder.StageState) error {
	panic("Not implemented yet")
}
