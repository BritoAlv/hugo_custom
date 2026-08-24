package discovery

import (
	"github.com/BritoAlv/hugo_custom/internal/utils"
)

type PublishedSet struct {
	Files []utils.Path
}

func Discover(root utils.Path, deployIgnore bool) (*PublishedSet, error) {
	panic("not implemented: discovery phase 1")
}