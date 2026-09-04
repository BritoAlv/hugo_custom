package discovery

import (
	"os"
	"path/filepath"
	"reflect"
	"testing"

	"github.com/BritoAlv/hugo_custom/internal/builder/contracts"
	"github.com/BritoAlv/hugo_custom/internal/utils"
)

func TestEncodeDotSegment(t *testing.T) {
	tests := []struct {
		name string
		in   string
		want string
	}{
		{"plain untouched", "notes", "notes"},
		{"interior dots untouched", "a.b", "a.b"},
		{"single leading dot", ".github", "dot-1-github"},
		{"double leading dots", "..x", "dot-2-x"},
		{"triple leading dots", "...", "dot-3-"},
		{"lone dot", ".", "dot-1-"},
		{"real marker word takes zero layer", "dot-1-x", "dot-0-dot-1-x"},
		{"marker without digits untouched", "dot-abc", "dot-abc"},
		{"empty untouched", "", ""},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := encodeDotSegment(tt.in); got != tt.want {
				t.Errorf("encodeDotSegment(%q) = %q; want %q", tt.in, got, tt.want)
			}
		})
	}
}

func TestDotSegmentRoundTrip(t *testing.T) {
	corpus := []string{
		"notes", "a.b", ".github", "..x", "...", ".", "..",
		"dot-1-x", "dot-0-dot-1-x", "dot-abc", "%2E", "café",
		".hidden", "well-known", "_index", "",
	}
	for _, in := range corpus {
		if got := decodeDotSegment(encodeDotSegment(in)); got != in {
			t.Errorf("round-trip(%q) = %q", in, got)
		}
	}
}

func TestDotSegmentInjective(t *testing.T) {
	inputs := []string{
		"env", ".env", "..env", "dot-1-env", "dot-0-dot-1-env",
		"github", ".github", "a", ".a", "..a", "...a",
	}
	seen := make(map[string]string, len(inputs))
	for _, in := range inputs {
		got := encodeDotSegment(in)
		if prev, dup := seen[got]; dup {
			t.Fatalf("collision: %q and %q both encode to %q", prev, in, got)
		}
		seen[got] = in
	}
}

func TestMapDotPaths(t *testing.T) {
	got, err := mapDotPaths([]utils.Path{"notes/a.md", ".hidden/b.md", ".gitignore"})
	if err != nil {
		t.Fatal(err)
	}
	want := []contracts.PublishedFile{
		{MappedPath: "notes/a.md", SourceRelativePath: "notes/a.md"},
		{MappedPath: "dot-1-hidden/b.md", SourceRelativePath: ".hidden/b.md"},
		{MappedPath: "dot-1-gitignore", SourceRelativePath: ".gitignore"},
	}
	if !reflect.DeepEqual(got, want) {
		t.Errorf("mapDotPaths() = %q; want %q", got, want)
	}
}

func TestMapDotPathsEmptyRel(t *testing.T) {
	if _, err := mapDotPaths([]utils.Path{""}); err == nil {
		t.Error("mapDotPaths(\"\") = nil error; want non-nil")
	}
}

func TestDiscoverMapsDotPaths(t *testing.T) {
	root := t.TempDir()
	src := filepath.Join(root, "src")
	write := func(rel, content string) {
		t.Helper()
		full := filepath.Join(src, rel)
		if err := os.MkdirAll(filepath.Dir(full), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(full, []byte(content), 0o644); err != nil {
			t.Fatal(err)
		}
	}
	write("notes/a.md", "# A\n")
	write(".hidden/b.md", "# B\n")
	write(".gitignore", "*.log\n")
	write("skip.log", "x")

	got, err := Discover(DiscoverInput{Root: root, ContentSource: src})
	if err != nil {
		t.Fatal(err)
	}
	want := []contracts.PublishedFile{
		{MappedPath: "dot-1-gitignore", SourceRelativePath: ".gitignore"},
		{MappedPath: "dot-1-hidden/b.md", SourceRelativePath: ".hidden/b.md"},
		{MappedPath: "notes/a.md", SourceRelativePath: "notes/a.md"},
	}
	if !reflect.DeepEqual(got.Files, want) {
		t.Errorf("Discover().Files = %q; want %q", got.Files, want)
	}
}
