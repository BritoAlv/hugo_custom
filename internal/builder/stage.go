package builder

import (
	"fmt"
	"os"

	"github.com/BritoAlv/hugo_custom/internal/config"
	"github.com/BritoAlv/hugo_custom/internal/utils"
)

type pluginContext struct {
	SiteConfig *config.SiteConfig
	Published  []utils.Path
}

type StageSummary struct {
	Nodes        int
	ContentFiles int
	StaticFiles  int
}

type sourceEntry struct {
	SourceRelativePath string
	Label              string
	Kind               string
	Body               string
}

func Stage(
	siteConfig *config.SiteConfig, published []utils.Path) (StageSummary, error) {

	stageDir := siteConfig.LocationConfig.StageDir
	err := os.RemoveAll(stageDir)
	if err != nil {
		return StageSummary{}, fmt.Errorf("stage: wiping %s: %w", stageDir, err)
	}
	err = os.MkdirAll(stageDir, 0o755)
	if err != nil {
		return StageSummary{}, fmt.Errorf("stage: creating %s: %w", stageDir, err)
	}

	pluginContext := pluginContext{SiteConfig: siteConfig, Published: published}

	var contents []sourceEntry
	for _, file_path := range published {
		for _, plugin := range defaultFilePlugins() {
			if !plugin.Handles(file_path) {
				continue
			}
			entry, err := plugin.Process(pluginContext, file_path)
			if err != nil {
				return StageSummary{}, fmt.Errorf("stage: %s failed on %s: %w", plugin.Name(), file_path, err)
			}
			if entry != nil {
				contents = append(contents, *entry)
			}
		}
	}
	for _, enricher := range defaultEnrichers() {
		err := enricher.Enrich(pluginContext, contents)
		if err != nil {
			return StageSummary{}, fmt.Errorf("stage: %s failed on %s", enricher.Name(), err)
		}
	}
	summary := StageSummary{}
	return summary, nil
}
