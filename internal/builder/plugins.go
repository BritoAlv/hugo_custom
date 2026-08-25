package builder

import "github.com/BritoAlv/hugo_custom/internal/utils"

type FilePluginInterface interface {
	Name() string
	Handles(src utils.Path) bool
	Process(input stageInput, state *stageState, src utils.Path) error
}

type EnricherPluginInterface interface {
	Name() string
	Enrich(input stageInput, state *stageState) error
}
