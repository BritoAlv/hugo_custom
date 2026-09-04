package utils

import (
	"os"
	"path/filepath"
	"reflect"
	"testing"
)

func TestReadLines(t *testing.T) {
	t.Run("skips empty lines", func(t *testing.T) {
		path := filepath.Join(t.TempDir(), "notes.txt")
		if err := os.WriteFile(path, []byte("one\n\ntwo\n\n"), 0o644); err != nil {
			t.Fatal(err)
		}
		if got, err := ReadLines(path); err != nil || !reflect.DeepEqual(got, []string{"one", "two"}) {
			t.Errorf("ReadLines() = %q, %v; want [one two], nil", got, err)
		}
	})

	t.Run("missing file returns nil without error", func(t *testing.T) {
		if got, err := ReadLines(filepath.Join(t.TempDir(), "absent.txt")); got != nil || err != nil {
			t.Errorf("ReadLines() = %q, %v; want nil, nil", got, err)
		}
	})

	t.Run("empty file returns nil without error", func(t *testing.T) {
		path := filepath.Join(t.TempDir(), "empty.txt")
		if err := os.WriteFile(path, nil, 0o644); err != nil {
			t.Fatal(err)
		}
		if got, err := ReadLines(path); got != nil || err != nil {
			t.Errorf("ReadLines() = %q, %v; want nil, nil", got, err)
		}
	})
}
