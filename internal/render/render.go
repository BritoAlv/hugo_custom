package render

import "github.com/BritoAlv/hugo_custom/internal/utils"

type RenderInput struct {
	ProjectRoot utils.Path
	StageDir    utils.Path
	OutputDir   utils.Path
}

func Render(input RenderInput) error {
	panic("not implemented: render phase 3")
}
