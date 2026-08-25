package builder

type AssetsEnricherPlugin struct{}

func (AssetsEnricherPlugin) Name() string {
	return "Assets Enricher Plugin"
}

func (AssetsEnricherPlugin) Enrich(input stageInput, state *stageState) error {
	panic("Not implemented yet")
}
