package builder

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"

	"github.com/BritoAlv/hugo_custom/internal/builder/contracts"
	"github.com/BritoAlv/hugo_custom/internal/config"
)

type StageSummary struct {
	Nodes        int
	ContentFiles int
	StaticFiles  int
}

func Stage(
	siteConfig *config.SiteConfig, published []contracts.PublishedFile) (StageSummary, error) {

	stageDir := siteConfig.LocationConfig.StageDir
	err := os.RemoveAll(stageDir)
	if err != nil {
		return StageSummary{}, fmt.Errorf("stage: wiping %s: %w", stageDir, err)
	}
	err = os.MkdirAll(stageDir, 0o755)
	if err != nil {
		return StageSummary{}, fmt.Errorf("stage: creating %s: %w", stageDir, err)
	}
	if err := writeDotPaths(stageDir, published); err != nil {
		return StageSummary{}, err
	}

	pluginContext := contracts.PluginContext{SiteConfig: siteConfig, Published: published}

	var contents []contracts.SourceEntry
	for _, file := range published {
		for _, plugin := range defaultFilePlugins() {
			if !plugin.Handles(file) {
				continue
			}
			entry, err := plugin.Process(pluginContext, file)
			if err != nil {
				return StageSummary{}, fmt.Errorf("stage: %s failed on %s: %w", plugin.Name(), file.SourceRelativePath, err)
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

func writeDotPaths(stageDir string, published []contracts.PublishedFile) error {
	mapped := make(map[string]string, len(published))
	for _, file := range published {
		mapped[file.SourceRelativePath] = file.MappedPath
	}
	data, err := json.Marshal(mapped)
	if err != nil {
		return fmt.Errorf("stage: encoding dotpaths: %w", err)
	}
	if err := os.MkdirAll(filepath.Join(stageDir, "data"), 0o755); err != nil {
		return fmt.Errorf("stage: creating data dir: %w", err)
	}
	if err := os.WriteFile(filepath.Join(stageDir, "data", "dotpaths.json"), data, 0o644); err != nil {
		return fmt.Errorf("stage: writing dotpaths: %w", err)
	}
	return nil
}
