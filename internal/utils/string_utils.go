package utils

import "strings"

func UnifyLists(list1 []string, list2 []string) []string {
	capacityHint := len(list1) + len(list2)
	seen := make(map[string]struct{}, capacityHint)
	unified := make([]string, 0, capacityHint)

	appendUnique := func(value string) {
		if value == "" {
			return
		}
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

func FirstNonEmptyLine(text string) string {
	for rawLine := range strings.SplitSeq(text, "\n") {
		if strings.TrimSpace(rawLine) != "" {
			return rawLine
		}
	}
	return ""
}