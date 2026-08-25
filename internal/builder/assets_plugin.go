package builder

type AssetsEnricherPlugin struct{}

func (AssetsEnricherPlugin) Name() string {
	return "Assets Enricher Plugin"
}

func (AssetsEnricherPlugin) Enrich(input StageInput, sources []sourceEntry) error {
	panic("Not implemented yet")
}
