package utils

import (
	"os"
	"path/filepath"
	"testing"
)

func TestWriteFile(t *testing.T) {
	t.Run("creates parents and round-trips content", func(t *testing.T) {
		target := filepath.Join(t.TempDir(), "sub", "deep", "a.md")
		if err := WriteContentToFile(target, "# Hi\n"); err != nil {
			t.Fatal(err)
		}
		got, err := os.ReadFile(target)
		if err != nil || string(got) != "# Hi\n" {
			t.Errorf("round-trip = %q, %v; want %q, nil", got, err, "# Hi\n")
		}
	})

	t.Run("overwrites existing content", func(t *testing.T) {
		target := filepath.Join(t.TempDir(), "a.md")
		if err := WriteContentToFile(target, "old"); err != nil {
			t.Fatal(err)
		}
		if err := WriteContentToFile(target, "new"); err != nil {
			t.Fatal(err)
		}
		got, _ := os.ReadFile(target)
		if string(got) != "new" {
			t.Errorf("round-trip = %q; want %q", got, "new")
		}
	})

	t.Run("writes anywhere, not only a content tree", func(t *testing.T) {
		target := filepath.Join(t.TempDir(), "static", "js", "app.js")
		if err := WriteContentToFile(target, "x"); err != nil {
			t.Fatal(err)
		}
		if _, err := os.Stat(target); err != nil {
			t.Errorf("Stat() = %v; want nil", err)
		}
	})
}
