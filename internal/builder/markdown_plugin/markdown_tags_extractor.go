package markdownplugin

import (
	"regexp"
	"strings"

	"github.com/yuin/goldmark"
	"github.com/yuin/goldmark/ast"
	"github.com/yuin/goldmark/text"
)

var mdParser = goldmark.New()
var inlineTagPattern = regexp.MustCompile(`(?:^|[^\p{L}\p{N}_/#])#([\p{L}\p{N}_/-]+)`)

// Inline tag spec (Obsidian-style `#tag`). A tag is exactly what this
// pattern matches (capture group 1), with trailing `/` trimmed:
// In words: `#` starts a tag at text start or after a char outside
// [letters, digits, `_`, `/`, `#`]; the body is 1+ of letters/digits/`_`/`-`/`/`.
// So `#hugo` and `(#hugo)` count, but `foo#bar`, `C#` and the `#frag` in
// `page#frag` don't; `#hugo,` yields `hugo`; `#project/active` stays whole.
// Case is preserved (`Go` != `go`); dedup is exact, order-preserving.
//
// Where to look is structural, not textual: each Paragraph/Heading/TextBlock
// contributes its visible text, while fenced/indented code blocks, inline
// code, HTML blocks, autolinks and image alt text are never scanned.

func appendIfAbsent(tags []string, seen map[string]struct{}, candidate string) []string {
	if _, repeated := seen[candidate]; repeated {
		return tags
	}
	seen[candidate] = struct{}{}
	return append(tags, candidate)
}

func extractInlineTags(body string) []string {
	source := []byte(body)
	doc := mdParser.Parser().Parse(text.NewReader(source))
	seen := make(map[string]struct{})
	var tags []string
	var buf strings.Builder

	flush := func() {
		for _, m := range inlineTagPattern.FindAllStringSubmatch(buf.String(), -1) {
			if tag := strings.TrimRight(m[1], "/"); tag != "" {
				tags = appendIfAbsent(tags, seen, tag)
			}
		}
		buf.Reset()
	}

	_ = ast.Walk(doc, func(node ast.Node, entering bool) (ast.WalkStatus, error) {
		switch node := node.(type) {
		case *ast.FencedCodeBlock, *ast.CodeBlock, *ast.CodeSpan, *ast.HTMLBlock, *ast.AutoLink, *ast.Image:
			if entering {
				return ast.WalkSkipChildren, nil
			}
		case *ast.Paragraph, *ast.Heading, *ast.TextBlock:
			if entering {
				buf.Reset()
			} else {
				flush()
			}
		case *ast.Text:
			if entering {
				buf.Write(node.Segment.Value(source))
				if node.SoftLineBreak() {
					buf.WriteByte('\n')
				}
			}
		}
		return ast.WalkContinue, nil
	})
	return tags
}
