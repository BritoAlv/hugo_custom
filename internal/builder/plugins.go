package builder

import "github.com/BritoAlv/hugo_custom/internal/utils"

type FilePluginInterface interface {
	Name() string
	Handles(src utils.Path) bool
	Process(input StageInput, state *StageState, src utils.Path) error
}

type EnricherPluginInterface interface {
	Name() string
	Enrich(input StageInput, state *StageState) error
}
