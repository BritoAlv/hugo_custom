package utils

import (
	"os"
	"path/filepath"
)

func CacheDir() Path {
	base := os.Getenv("XDG_CACHE_HOME")
	if base == "" {
		if home, err := os.UserHomeDir(); err == nil {
			base = filepath.Join(home, ".cache")
		}
	}
	return Path(filepath.Join(base, "hugo_custom"))
}