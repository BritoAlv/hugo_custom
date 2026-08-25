package plugins

import (
	"path/filepath"
	"strings"

	"github.com/BritoAlv/hugo_custom/internal/builder"
	"github.com/BritoAlv/hugo_custom/internal/utils"
)

type MarkdownPlugin struct {}

func (MarkdownPlugin) Name() string { return "Markdown Plugin"}

func (MarkdownPlugin) Handles(src utils.Path) bool {
	return strings.EqualFold(filepath.Ext(src), ".md")
}

func (MarkdownPlugin) Process(input builder.StageInput, state *builder.StageState, src utils.Path) error {
	panic("Not implemented Yet")
} 