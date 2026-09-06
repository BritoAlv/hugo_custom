package discovery

import (
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/BritoAlv/hugo_custom/internal/builder/contracts"
	"github.com/BritoAlv/hugo_custom/internal/utils"
)

// readMetadata gathers the facts for a single file: filesystem modification
// time (required) plus git info (optional, nil when untracked). It returns a
// complete Metadata value; callers assemble it into a PublishedFile.
func readMetadata(root utils.Path, contentSource utils.Path, sourceRelativePath utils.Path) (contracts.Metadata, error) {
	absolutePath := filepath.Join(contentSource, sourceRelativePath)
	fileInfo, err := os.Stat(absolutePath)
	if err != nil {
		return contracts.Metadata{}, fmt.Errorf("discovery: stating %s: %w", sourceRelativePath, err)
	}
	return contracts.Metadata{
		ModTime: fileInfo.ModTime().UTC().Format(time.RFC3339),
		Git:     utils.ReadGitInfo(root, absolutePath),
	}, nil
}
