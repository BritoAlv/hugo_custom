package utils

import (
	"errors"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"slices"
	"strings"
)

func ReadLines(path Path) ([]string, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		if errors.Is(err, fs.ErrNotExist) {
			return nil, nil
		}
		return nil, fmt.Errorf("utils: reading %s: %w", path, err)
	}
	var lines []string
	for rawLine := range strings.SplitSeq(string(data), "\n") {
		if rawLine == "" {
			continue
		}
		lines = append(lines, rawLine)
	}
	return lines, nil
}

func RelativeToRoot(root Path, absoluteTarget Path) (Path, error) {
	relativePath, err := filepath.Rel(root, absoluteTarget)
	if err != nil {
		return "", fmt.Errorf("utils: relativizing %s: %w", absoluteTarget, err)
	}
	if relativePath == "." {
		return "", nil
	}
	return filepath.ToSlash(relativePath), nil
}

func Walk(pathToWalk Path, excludedDirs []string) ([]Path, error) {
	var files []Path
	err := filepath.WalkDir(pathToWalk, func(currentPath string, entry fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if entry.IsDir() {
			if slices.Contains(excludedDirs, entry.Name()) {
				return fs.SkipDir
			}
			return nil
		}
		relativePath, err := RelativeToRoot(pathToWalk, currentPath)
		if err != nil {
			return err
		}
		files = append(files, Path(relativePath))
		return nil
	})
	if err != nil {
		return nil, fmt.Errorf("utils: walking %s: %w", pathToWalk, err)
	}
	return files, nil
}

func WriteContentToFile(absoluteTargetPath Path, content string) error {
	if err := os.MkdirAll(filepath.Dir(absoluteTargetPath), 0o755); err != nil {
		return fmt.Errorf("utils: creating parent of %s: %w", absoluteTargetPath, err)
	}
	if err := os.WriteFile(absoluteTargetPath, []byte(content), 0o644); err != nil {
		return fmt.Errorf("utils: writing %s: %w", absoluteTargetPath, err)
	}
	return nil
}
