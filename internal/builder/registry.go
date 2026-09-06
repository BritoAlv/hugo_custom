package builder

import (
	"github.com/BritoAlv/hugo_custom/internal/builder/contracts"
	"github.com/BritoAlv/hugo_custom/internal/builder/markdown_plugin"
)

func defaultFilePlugins() []contracts.FilePluginInterface {
	return []contracts.FilePluginInterface{markdownplugin.MarkdownPlugin{}}
}

func defaultEnrichers() []contracts.EnricherPluginInterface {
	return []contracts.EnricherPluginInterface{}
}
