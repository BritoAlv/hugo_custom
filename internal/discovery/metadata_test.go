package discovery

import (
	"os"
	"os/exec"
	"path/filepath"
	"testing"
)

func writeFile(t *testing.T, base, rel, content string) {
	t.Helper()
	full := filepath.Join(base, rel)
	if err := os.MkdirAll(filepath.Dir(full), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(full, []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
}

func TestReadMetadataUntracked(t *testing.T) {
	root := t.TempDir()
	src := filepath.Join(root, "src")
	writeFile(t, src, "notes/a.md", "# A\n")

	meta, err := readMetadata(root, src, "notes/a.md")
	if err != nil {
		t.Fatal(err)
	}
	if meta.LastModificationDate == "" {
		t.Error("Metadata.ModTime is empty; want non-empty")
	}
	if meta.Git != nil {
		t.Errorf("Metadata.Git = %+v; want nil (temp dir outside git)", meta.Git)
	}
}

func TestReadMetadataTracked(t *testing.T) {
	if _, err := exec.LookPath("git"); err != nil {
		t.Skip("git not available")
	}
	root := t.TempDir()
	src := filepath.Join(root, "src")
	writeFile(t, src, "notes/a.md", "# A\n")

	for _, args := range [][]string{
		{"init"},
		{"config", "user.email", "test@example.com"},
		{"config", "user.name", "Test"},
		{"add", "-A"},
		{"commit", "-m", "init"},
	} {
		cmd := exec.Command("git", args...)
		cmd.Dir = root
		if out, err := cmd.CombinedOutput(); err != nil {
			t.Fatalf("git %v: %v\n%s", args, err, out)
		}
	}

	meta, err := readMetadata(root, src, "notes/a.md")
	if err != nil {
		t.Fatal(err)
	}
	if meta.LastModificationDate == "" {
		t.Error("Metadata.ModTime is empty; want non-empty")
	}
	if meta.Git == nil {
		t.Fatal("Metadata.Git is nil; want non-nil for tracked file")
	}
	if len(meta.Git.LastCommit.CommitHash) != 40 {
		t.Errorf("CommitHash len = %d; want 40 (no truncation)", len(meta.Git.LastCommit.CommitHash))
	}
	if meta.Git.LastCommit.Author != "Test" {
		t.Errorf("Author = %q; want %q", meta.Git.LastCommit.Author, "Test")
	}
}

func TestReadMetadataMissingFile(t *testing.T) {
	root := t.TempDir()
	src := filepath.Join(root, "src")
	if err := os.MkdirAll(src, 0o755); err != nil {
		t.Fatal(err)
	}
	if _, err := readMetadata(root, src, "nope.md"); err == nil {
		t.Error("readMetadata(missing) = nil error; want non-nil")
	}
}

func TestDiscoverEnrichesMetadata(t *testing.T) {
	root := t.TempDir()
	src := filepath.Join(root, "src")
	writeFile(t, src, "notes/a.md", "# A\n")
	writeFile(t, src, "notes/b.md", "# B\n")

	got, err := Discover(DiscoverInput{Root: root, ContentSource: src})
	if err != nil {
		t.Fatal(err)
	}
	if len(got.Files) != 2 {
		t.Fatalf("Discover().Files len = %d; want 2", len(got.Files))
	}
	for i := range got.Files {
		if got.Files[i].Metadata.LastModificationDate == "" {
			t.Errorf("Discover().Files[%d].Metadata.ModTime is empty; want non-empty", i)
		}
		if got.Files[i].Metadata.Git != nil {
			t.Errorf("Discover().Files[%d].Metadata.Git = %+v; want nil (temp dir outside git)", i, got.Files[i].Metadata.Git)
		}
	}
}
