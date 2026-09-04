package utils

import (
	"os"
	"path/filepath"
	"reflect"
	"testing"
)

func TestWalk(t *testing.T) {
	root := t.TempDir()
	write := func(rel string) {
		t.Helper()
		full := filepath.Join(root, rel)
		if err := os.MkdirAll(filepath.Dir(full), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(full, []byte("x"), 0o644); err != nil {
			t.Fatal(err)
		}
	}
	write("a.md")
	write("sub/b.md")
	write("skip/c.md")
	write("sub/skip-deep/d.md")

	t.Run("lists files relative in lexical order, skipping excluded dirs", func(t *testing.T) {
		got, err := Walk(root, []string{"skip", "skip-deep"})
		want := []Path{"a.md", "sub/b.md"}
		if err != nil || !reflect.DeepEqual(got, want) {
			t.Errorf("Walk() = %q, %v; want %q, nil", got, err, want)
		}
	})

	t.Run("no exclusions lists everything", func(t *testing.T) {
		got, err := Walk(root, nil)
		want := []Path{"a.md", "skip/c.md", "sub/b.md", "sub/skip-deep/d.md"}
		if err != nil || !reflect.DeepEqual(got, want) {
			t.Errorf("Walk() = %q, %v; want %q, nil", got, err, want)
		}
	})

	t.Run("missing root returns error", func(t *testing.T) {
		if _, err := Walk(filepath.Join(root, "absent"), nil); err == nil {
			t.Error("Walk() = nil error; want non-nil")
		}
	})
}
