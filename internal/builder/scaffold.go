package builder

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/BritoAlv/hugo_custom/internal/config"
	"github.com/BritoAlv/hugo_custom/internal/utils"
	"github.com/BurntSushi/toml"
)

const templatesRelativePath = "src/hugo_custom/templates"

func scaffoldHugoProject(stageDir utils.Path, siteConfig *config.SiteConfig) error {
	templatesPath := filepath.Join(siteConfig.LocationConfig.ProjectRoot, templatesRelativePath)

	if err := os.CopyFS(
		filepath.Join(stageDir, "layouts"),
		os.DirFS(filepath.Join(templatesPath, "layouts")),
	); err != nil {
		return fmt.Errorf("stage: copying layouts: %w", err)
	}
	return writeHugoConfig(stageDir, filepath.Join(templatesPath, "hugo.toml"), siteConfig)
}

func writeHugoConfig(stageDir utils.Path, sourceConfigPath string, siteConfig *config.SiteConfig) error {
	hugoConfig := map[string]any{}
	if _, err := toml.DecodeFile(sourceConfigPath, &hugoConfig); err != nil {
		return fmt.Errorf("stage: decoding %s: %w", sourceConfigPath, err)
	}

	hugoConfig["title"] = siteConfig.SiteMeta.Title
	hugoConfig["baseURL"] = siteConfig.SiteMeta.SiteURL

	params, _ := hugoConfig["params"].(map[string]any)
	if params == nil {
		params = map[string]any{}
	}

	if siteConfig.SiteMeta.HomePageMarkdown != "" {
		params["homepage"] = siteConfig.SiteMeta.HomePageMarkdown
	}
	hugoConfig["params"] = params

	output, err := toml.Marshal(hugoConfig)
	if err != nil {
		return fmt.Errorf("stage: enconding hugo.toml: %w", err)
	}
	return os.WriteFile(filepath.Join(stageDir, "hugo.toml"), output, 0o644)
}