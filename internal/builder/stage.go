package builder

import (
	"fmt"
	"os"

	"github.com/BritoAlv/hugo_custom/internal/builder/contracts"
	"github.com/BritoAlv/hugo_custom/internal/config"
	"github.com/BritoAlv/hugo_custom/internal/utils"
)



type StageSummary struct {
	Nodes        int
	ContentFiles int
	StaticFiles  int
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

	pluginContext := contracts.PluginContext{SiteConfig: siteConfig, Published: published}

	var contents []contracts.SourceEntry
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

	if err := scaffoldHugoProject(stageDir, siteConfig); err != nil {
		return StageSummary{}, fmt.Errorf("stage: scaffolding: %w", err)
	}

	summary := StageSummary{}
	return summary, nil
}
