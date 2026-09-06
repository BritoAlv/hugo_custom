package discovery

import (
	"fmt"
	"regexp"
	"strconv"
	"strings"

	"github.com/BritoAlv/hugo_custom/internal/utils"
)

var dotMarkerPattern = regexp.MustCompile(`^dot-([0-9]+)-(.*)$`)

func encodeDotSegment(segment string) string {
	rest := strings.TrimLeft(segment, ".")
	dots := len(segment) - len(rest)
	if dots == 0 && !dotMarkerPattern.MatchString(segment) {
		return segment
	}
	return "dot-" + strconv.Itoa(dots) + "-" + rest
}

func decodeDotSegment(segment string) string {
	m := dotMarkerPattern.FindStringSubmatch(segment)
	if m == nil {
		return segment
	}
	dots, err := strconv.Atoi(m[1])
	if err != nil {
		return segment
	}
	if dots == 0 {
		return m[2]
	}
	return strings.Repeat(".", dots) + m[2]
}

func encodeDotPath(sourceRelativePath utils.Path) utils.Path {
	segments := strings.Split(sourceRelativePath, "/")
	for index, segment := range segments {
		segments[index] = encodeDotSegment(segment)
	}
	return utils.Path(strings.Join(segments, "/"))
}

// dotMapping is the pipeline-internal result of path encoding: the source
// path plus its dot-encoded mapped path, before metadata is attached.
type dotMapping struct {
	source utils.Path
	mapped utils.Path
}

func mapDotPaths(sourceRelativePaths []utils.Path) ([]dotMapping, error) {
	mappings := make([]dotMapping, 0, len(sourceRelativePaths))
	for _, sourceRelativePath := range sourceRelativePaths {
		mappedPath := encodeDotPath(sourceRelativePath)
		if mappedPath == "" {
			return nil, fmt.Errorf("discovery: %q maps to an empty mapped path", sourceRelativePath)
		}
		mappings = append(mappings, dotMapping{source: sourceRelativePath, mapped: mappedPath})
	}
	return mappings, nil
}
