package builder

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/BritoAlv/hugo_custom/internal/builder/contracts"
)

func TestWriteDotPaths(t *testing.T) {
	t.Run("stages every file including unchanged ones", func(t *testing.T) {
		stageDir := t.TempDir()
		published := []contracts.PublishedFile{
			{MappedPath: "notes/a.md", SourceRelativePath: "notes/a.md"},
			{MappedPath: "dot-1-hidden/b.md", SourceRelativePath: ".hidden/b.md"},
		}
		if err := writeDotPaths(stageDir, published); err != nil {
			t.Fatal(err)
		}
		got, err := os.ReadFile(filepath.Join(stageDir, "data", "dotpaths.json"))
		if err != nil {
			t.Fatal(err)
		}
		want := `{".hidden/b.md":"dot-1-hidden/b.md","notes/a.md":"notes/a.md"}`
		if string(got) != want {
			t.Errorf("dotpaths.json = %s; want %s", got, want)
		}
	})

	t.Run("dotless files map to themselves", func(t *testing.T) {
		stageDir := t.TempDir()
		published := []contracts.PublishedFile{
			{MappedPath: "notes/a.md", SourceRelativePath: "notes/a.md"},
		}
		if err := writeDotPaths(stageDir, published); err != nil {
			t.Fatal(err)
		}
		got, err := os.ReadFile(filepath.Join(stageDir, "data", "dotpaths.json"))
		if err != nil || string(got) != `{"notes/a.md":"notes/a.md"}` {
			t.Errorf("dotpaths.json = %q, %v; want %q, nil", got, err, `{"notes/a.md":"notes/a.md"}`)
		}
	})
}
