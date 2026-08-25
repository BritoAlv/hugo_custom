package builder

func defaultFilePlugins() []FilePluginInterface {
	return []FilePluginInterface {MarkdownPlugin{}}
}

func defaultEnrichers() []EnricherPluginInterface {
	return []EnricherPluginInterface{
		AssetsEnricherPlugin{},
	}
}