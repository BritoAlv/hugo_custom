package discovery

import (
	"github.com/BritoAlv/hugo_custom/internal/builder/contracts"
	"github.com/BritoAlv/hugo_custom/internal/utils"
)

type DiscoverInput struct {
	Root           utils.Path
	ContentSource  utils.Path
	ConfigFileName utils.Path
	DeployIgnore   bool
}

type PublishedSet struct {
	Files []contracts.PublishedFile
}

func Discover(discoverInput DiscoverInput) (*PublishedSet, error) {
	candidates, err := utils.Walk(discoverInput.ContentSource, []string{".git"})
	if err != nil {
		return nil, err
	}
	foundGitignores, err := findGitignores(discoverInput.Root, discoverInput.ContentSource, candidates)
	if err != nil {
		return nil, err
	}
	specs, err := loadSpecs(discoverInput.Root, discoverInput.DeployIgnore, foundGitignores)
	if err != nil {
		return nil, err
	}
	survivors, err := filter(discoverInput.Root, discoverInput.ContentSource, candidates, specs)
	if err != nil {
		return nil, err
	}
	mappings, err := mapDotPaths(survivors)
	if err != nil {
		return nil, err
	}
	files := make([]contracts.PublishedFile, 0, len(mappings))
	for _, mapping := range mappings {
		metadata, err := readMetadata(discoverInput.Root, discoverInput.ContentSource, mapping.source)
		if err != nil {
			return nil, err
		}
		files = append(files, contracts.PublishedFile{
			SourceRelativePath: mapping.source,
			MappedPath:         mapping.mapped,
			Metadata:           metadata,
		})
	}
	return &PublishedSet{Files: files}, nil
}
