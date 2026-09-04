package utils

import (
	"fmt"
	"strings"
)

func UnifyLists[T comparable](list1 []T, list2 []T) []T {
	capacityHint := len(list1) + len(list2)
	seen := make(map[T]struct{}, capacityHint)
	unified := make([]T, 0, capacityHint)

	appendUnique := func(value T) {
		if _, repeated := seen[value]; repeated {
			return
		}
		seen[value] = struct{}{}
		unified = append(unified, value)
	}

	for _, value := range list1 {
		appendUnique(value)
	}
	for _, value := range list2 {
		appendUnique(value)
	}
	return unified
}

func FirstNonEmptyLine(text string) (string, error) {
	for rawLine := range strings.SplitSeq(text, "\n") {
		if strings.TrimSpace(rawLine) != "" {
			return rawLine, nil
		}
	}
	return "", fmt.Errorf("Text is empty")
}
