package discovery

import (
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/BritoAlv/hugo_custom/internal/builder/contracts"
	"github.com/BritoAlv/hugo_custom/internal/utils"
)

func readMetadata(root utils.Path, contentSource utils.Path, sourceRelativePath utils.Path) (contracts.Metadata, error) {
	absolutePath := filepath.Join(contentSource, sourceRelativePath)
	fileInfo, err := os.Stat(absolutePath)
	if err != nil {
		return contracts.Metadata{}, fmt.Errorf("discovery: stating %s: %w", sourceRelativePath, err)
	}
	return contracts.Metadata{
		LastModificationDate: fileInfo.ModTime().UTC().Format(time.RFC3339),
		Git:                  utils.ReadGitInfo(root, absolutePath),
	}, nil
}
