package markdownplugin

import (
	"regexp"
	"strings"

	"github.com/BritoAlv/hugo_custom/internal/builder/contracts"
	"github.com/goccy/go-yaml"
)

type markdownFrontMatter struct {
	Title string   `yaml:"title"`
	Tags  []string `yaml:"tags"`
}

var frontMatterBlockPattern = regexp.MustCompile(`(?s)^---[ \t]*\n(.*?)\n---[ \t]*(?:\n|$)`)

func splitFrontMatterBody(text string) (markdownFrontMatter, string) {
	block := frontMatterBlockPattern.FindStringSubmatch(text)
	if block == nil {
		return markdownFrontMatter{}, text
	}
	var parsedMeta markdownFrontMatter
	if err := yaml.Unmarshal([]byte(block[1]), &parsedMeta); err != nil {
		return markdownFrontMatter{}, text
	}
	return parsedMeta, text[len(block[0]):]
}

type hugoFrontMatter struct {
	Title                string   `yaml:"title,omitempty"`
	LastModificationDate string   `yaml:"lastmod,omitempty"`
	Tags                 []string `yaml:"tags,omitempty"`
	LastCommit           string   `yaml:"lastcommit,omitempty"`
	LastCommitAuthor     string   `yaml:"lastcommit_author,omitempty"`
	LastCommitDate       string   `yaml:"lastcommit_date,omitempty"`
	SourceRelativePath   string   `yaml:"source_relative_path"`
}

func frontMatterGit(fileMeta contracts.Metadata) (commit, author, date string) {
	if fileMeta.Git == nil {
		return "", "", ""
	}
	return fileMeta.Git.LastCommit.CommitHash, fileMeta.Git.LastCommit.Author, fileMeta.Git.LastCommit.CommitDate
}

func serializeFrontMatter(file contracts.PublishedFile, derivedContent derivedMarkdownMeta) string {
	lastCommit, lastCommitAuthor, lastCommitDate := frontMatterGit(file.Metadata)
	staged := hugoFrontMatter{
		Title:                derivedContent.title,
		LastModificationDate: file.Metadata.LastModificationDate,
		Tags:                 derivedContent.tags,
		LastCommit:           lastCommit,
		LastCommitAuthor:     lastCommitAuthor,
		LastCommitDate:       lastCommitDate,
		SourceRelativePath:   file.SourceRelativePath,
	}

	dump, err := yaml.Marshal(staged)
	if err != nil {
		return ""
	}
	return "---\n" + strings.TrimRight(string(dump), "\n") + "\n---\n\n"
}

type derivedMarkdownMeta struct {
	title string
	tags  []string
}
