package discovery

import (
	"github.com/BritoAlv/hugo_custom/internal/utils"
)

type DiscoverInput struct {
	Root utils.Path
	ContentSource utils.Path
	ConfigFileName utils.Path
	DeployIgnore bool
}

type PublishedSet struct {
	Files []utils.Path
}

func Discover(discoverInput DiscoverInput) (*PublishedSet, error) {
	panic("not implemented: discovery phase 1")
}