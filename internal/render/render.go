package render

import (
	"fmt"
	"os"
	"os/exec"

	"github.com/BritoAlv/hugo_custom/internal/utils"
)

type RenderInput struct {
	ProjectRoot utils.Path
	StageDir    utils.Path
	OutputDir   utils.Path
}

func Render(input RenderInput) error {
	if err := os.RemoveAll(input.OutputDir); err != nil {
		return fmt.Errorf("render: clearing %s: %w", input.OutputDir, err)
	}
	command := exec.Command("hugo", "--source", input.StageDir, "--destination", input.OutputDir)
	command.Dir = input.ProjectRoot
	output, err := command.CombinedOutput()
	if err != nil {
		return fmt.Errorf("render: hugo failed: %w\n%s", err, output)
	}
	return nil
}
