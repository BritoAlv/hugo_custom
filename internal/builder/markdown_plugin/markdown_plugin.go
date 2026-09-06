package markdownplugin

import (
	"fmt"
	"os"
	"path/filepath"
	"slices"
	"strings"

	"github.com/BritoAlv/hugo_custom/internal/builder/contracts"
	"github.com/BritoAlv/hugo_custom/internal/utils"
)

const kindMarkdown = "md"

type MarkdownPlugin struct{}

func (MarkdownPlugin) Name() string { return "Markdown Plugin" }

func (MarkdownPlugin) Handles(file contracts.PublishedFile) bool {
	return strings.EqualFold(filepath.Ext(file.SourceRelativePath), "."+kindMarkdown)
}

func (MarkdownPlugin) Process(input contracts.PluginContext, file contracts.PublishedFile) (*contracts.SourceEntry, error) {
	sourceRoot := input.SiteConfig.LocationConfig.ContentSource
	absolutePath := filepath.Join(sourceRoot, file.SourceRelativePath)

	rawText, err := os.ReadFile(absolutePath)
	if err != nil {
		return nil, fmt.Errorf("markdown plugin: reading %s: %w", file.SourceRelativePath, err)
	}
	parsedMeta, body := splitFrontMatterBody(string(rawText))
	bodyTags := extractInlineTags(body)

	unifiedTags := utils.UnifyLists(parsedMeta.Tags, bodyTags)
	unifiedTags = slices.DeleteFunc(unifiedTags, func(s string) bool { return s == "" })

	resolvedTitle := parsedMeta.Title
	if resolvedTitle == "" {
		resolvedTitle, err = utils.FirstNonEmptyLine(body)
		if err != nil {
			resolvedTitle = strings.TrimSuffix(filepath.Base(file.SourceRelativePath), filepath.Ext(file.SourceRelativePath))
		} else {
			resolvedTitle = strings.TrimLeft(resolvedTitle, "#")
			resolvedTitle = strings.TrimLeft(resolvedTitle, " ")
		}
	}

	entry := &contracts.SourceEntry{
		SourceRelativePath: file.SourceRelativePath,
		Label:              resolvedTitle,
		Kind:               kindMarkdown,
		Body:               body,
	}

	derived := derivedMarkdownMeta{
		title: resolvedTitle,
		tags:  unifiedTags,
	}
	stagedContent := serializeFrontMatter(file, derived) + body
	if err := input.WriteContent(file.MappedPath, stagedContent); err != nil {
		return nil, err
	}
	return entry, nil
}
