package utils

import (
	"fmt"
	"os/exec"
	"strings"
)

type CommitInfo struct {
	CommitHash string
	Author     string
	CommitDate string
}

func runGit(root Path, arguments ...string) (string, error) {
	command := exec.Command("git", arguments...)
	command.Dir = root
	output, err := command.Output()
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(string(output)), nil
}

func fetchCommit(root Path, path string, revision ...string) (CommitInfo, bool) {
	args := append([]string{"log"}, append(revision, "--format=%H%x09%an%x09%aI", "--", path)...)
	output, err := runGit(root, args...)
	if err != nil || output == "" {
		return CommitInfo{}, false
	}
	parts := strings.Split(output, "\t")
	if len(parts) != 3 || parts[0] == "" {
		return CommitInfo{}, false
	}
	return CommitInfo{CommitHash: parts[0], Author: parts[1], CommitDate: parts[2]}, true
}

func ReadLastCommitMeta(root Path, absoluteFilePath string) (CommitInfo, error) {
	last, found := fetchCommit(root, absoluteFilePath, "-1")
	if !found {
		return CommitInfo{}, fmt.Errorf("could not find last commit for %s", absoluteFilePath)
	}
	return last, nil
}
