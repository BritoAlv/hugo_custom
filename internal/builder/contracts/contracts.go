package contracts

import (
	"path/filepath"

	"github.com/BritoAlv/hugo_custom/internal/config"
	"github.com/BritoAlv/hugo_custom/internal/utils"
)

type FilePluginInterface interface {
	Name() string
	Handles(file PublishedFile) bool
	Process(input PluginContext, file PublishedFile) (*SourceEntry, error)
}

type EnricherPluginInterface interface {
	Name() string
	Enrich(input PluginContext, sources []SourceEntry) error
}

type PluginContext struct {
	SiteConfig *config.SiteConfig
	Published  []PublishedFile
}

func (input PluginContext) WriteContent(rel string, content string) error {
	return utils.WriteContentToFile(
		filepath.Join(input.SiteConfig.LocationConfig.StageDir, "content", rel),
		content,
	)
}

type PublishedFile struct {
	SourceRelativePath utils.Path // path relative to content source.
	MappedPath         utils.Path // dot-encoded path that hugo stages and serves.
	Metadata           Metadata   // filesystem + git facts collected once in discovery.
}

type Metadata struct {
	LastModificationDate string // filesystem modification time, RFC3339 UTC. Always set.
	Git                  *utils.GitInfo
}

type SourceEntry struct {
	SourceRelativePath utils.Path
	Label              string
	Kind               string
	Body               string
}
