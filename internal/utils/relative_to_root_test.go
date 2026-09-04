package utils

import (
	"testing"
)

func TestRelativeToRoot(t *testing.T) {
	tests := []struct {
		name    string
		root    Path
		target  string
		want    string
		wantErr bool
	}{
		{"child file", "/site/source", "/site/source/notes/a.md", "notes/a.md", false},
		{"root itself collapses to empty", "/site/source", "/site/source", "", false},
		{"separators become slashes", "/site/source", "/site/source/a/b.md", "a/b.md", false},
		{"outside root escapes with dot-dot", "/site/source", "/site/other.md", "../other.md", false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := RelativeToRoot(tt.root, tt.target)
			if (err != nil) != tt.wantErr || got != tt.want {
				t.Errorf("RelativeToRoot() = %q, %v; want %q, err=%v", got, err, tt.want, tt.wantErr)
			}
		})
	}
}
