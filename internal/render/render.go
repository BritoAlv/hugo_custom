package render

import "github.com/BritoAlv/hugo_custom/internal/utils"

type Input struct {
	ProjectRoot utils.Path
	StageDir utils.Path
	OutputDir utils.Path
}

func Render(input Input) error {
	panic("not implemented: render phase 3")
}