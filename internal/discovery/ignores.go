package discovery

import (
	"errors"
	"fmt"
	"io/fs"
	"os"
	"path"
	"path/filepath"
	"strings"

	"github.com/BritoAlv/hugo_custom/internal/utils"
	"github.com/go-git/go-git/v6/plumbing/format/gitignore"
)

type ignoreSpec struct {
	base    string
	matcher gitignore.Matcher
}

func findGitignores(rootPath utils.Path, contentSourcePath utils.Path, sourceRelativeCandidateFiles []utils.Path) ([]utils.Path, error) {
	rootGitignore := utils.Path(filepath.Join(rootPath, ".gitignore"))
	sameTree := contentSourcePath == rootPath

	var found []utils.Path

	_, statErr := os.Stat(rootGitignore)
	switch {
	case statErr == nil:
		found = append(found, rootGitignore)
	case !errors.Is(statErr, fs.ErrNotExist):
		return nil, fmt.Errorf("discovery: stat %s: %w", rootGitignore, statErr)
	}

	for _, candidate := range sourceRelativeCandidateFiles {
		if path.Base(candidate) != ".gitignore" {
			continue
		}
		if sameTree && candidate == ".gitignore" {
			continue
		}
		absolutePath := filepath.Join(contentSourcePath, candidate)
		found = append(found, utils.Path(absolutePath))
	}
	return found, nil
}

func loadSpecs(rootPath utils.Path, includeSiteIgnore bool, absoluteGitignorePaths []utils.Path) ([]ignoreSpec, error) {
	var specs []ignoreSpec
	for _, absoluteGitignore := range absoluteGitignorePaths {
		base, err := utils.RelativeToRoot(rootPath, filepath.Dir(absoluteGitignore))
		if err != nil {
			return nil, err
		}
		spec, err := compileIgnoreFile(base, absoluteGitignore)
		if err != nil {
			return nil, err
		}
		if spec.matcher != nil {
			specs = append(specs, spec)
		}
	}
	if includeSiteIgnore {
		siteIgnorePath := filepath.Join(rootPath, ".siteignore")
		siteSpec, err := compileIgnoreFile("", siteIgnorePath)
		if err != nil {
			return nil, err
		}
		if siteSpec.matcher != nil {
			specs = append(specs, siteSpec)
		}
	}
	return specs, nil
}

func compileIgnoreFile(baseDirectoryRelativeToRoot string, absoluteIgnoreFilePath utils.Path) (ignoreSpec, error) {
	lines, err := utils.ReadLines(absoluteIgnoreFilePath)
	if err != nil || len(lines) == 0 {
		return ignoreSpec{}, err
	}
	filteredLines := make([]string, 0)
	for _, line := range lines {
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		filteredLines = append(filteredLines, line)
	}
	lines = filteredLines
	patterns := make([]gitignore.Pattern, 0, len(lines))
	for _, line := range lines {
		patterns = append(patterns, gitignore.ParsePattern(line, nil))
	}
	return ignoreSpec{base: baseDirectoryRelativeToRoot, matcher: gitignore.NewMatcher(patterns)}, nil
}

func filter(rootPath utils.Path, contentSourcePath utils.Path, sourceRelativeCandidates []utils.Path, specs []ignoreSpec) ([]utils.Path, error) {
	survivors := make([]utils.Path, 0, len(sourceRelativeCandidates))
	for _, candidate := range sourceRelativeCandidates {
		absolutePath := filepath.Join(contentSourcePath, candidate)
		rootRelativePosix, err := utils.RelativeToRoot(rootPath, absolutePath)
		if err != nil {
			return nil, err
		}
		if !isIgnored(rootRelativePosix, specs) {
			survivors = append(survivors, candidate)
		}
	}
	return survivors, nil
}

func relativeToSpecBase(specBase string, rootRelativePosixPath string) (string, bool) {
	if specBase == "" {
		return rootRelativePosixPath, true
	}
	if after, ok :=strings.CutPrefix(rootRelativePosixPath, specBase+"/"); ok  {
		return after, true
	}
	return "", false
}

func isIgnored(rootRelativePosixPath string, ignoreSpecs []ignoreSpec) bool {
	for _, spec := range ignoreSpecs {
		specRelativePath, withinScope := relativeToSpecBase(spec.base, rootRelativePosixPath)
		if !withinScope{
			continue
		}
		if spec.matcher.Match(strings.Split(specRelativePath, "/"), false) {
			return true
		}
	}
	return false
}
