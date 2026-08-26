package utils

import (
	"fmt"
	"os/exec"
	"strings"
)

type GitInfo struct {
	CreatedDate string
	CommitHash  string
	Author      string
	CommitDate  string
}

type CommitInfo struct {
	HashFull  string
	Author    string
	DateStamp string
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
	return CommitInfo{HashFull: parts[0], Author: parts[1], DateStamp: parts[2]}, true
}

func ReadGitInfo(root Path, absoluteFilePath string) (GitInfo, error) {
	gitInfo := GitInfo{}

	first, found := fetchCommit(root, absoluteFilePath, "--reverse", "-1")
	if !found {
		return GitInfo{}, fmt.Errorf("could not find first commit for %s", absoluteFilePath)
	}
	gitInfo.CreatedDate = first.DateStamp

	last, found := fetchCommit(root, absoluteFilePath, "-1")
	if !found {
		return GitInfo{}, fmt.Errorf("could not find last commit for %s", absoluteFilePath)
	}
	gitInfo.CommitHash = last.HashFull
	gitInfo.Author = last.Author
	gitInfo.CommitDate = last.DateStamp

	return gitInfo, nil
}