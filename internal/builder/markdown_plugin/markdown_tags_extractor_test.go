package markdownplugin

import (
	"reflect"
	"testing"
)

func TestExtractInlineTags(t *testing.T) {
	tests := []struct {
		name string
		body string
		want []string
	}{
		{
			name: "basic inline tag",
			body: "# Title\n\nHello #hugo world\n",
			want: []string{"hugo"},
		},
		{
			name: "multiple tags one line",
			body: "Tagged #a #b #c.\n",
			want: []string{"a", "b", "c"},
		},
		{
			name: "heading marker is not a tag",
			body: "# Title\n\n## Section\n",
			want: nil,
		},
		{
			name: "tag in heading counts",
			body: "## Notes #review\n",
			want: []string{"review"},
		},
		{
			name: "fenced code ignored",
			body: "# T\n\n```sh\n#evil\n```\n\n~~~text\n#alsono\n~~~\n\n#ok\n",
			want: []string{"ok"},
		},
		{
			name: "indented code ignored",
			body: "Para.\n\n    #evil\n\n#ok\n",
			want: []string{"ok"},
		},
		{
			name: "inline code ignored",
			body: "Use `#evil` and #ok.\n",
			want: []string{"ok"},
		},
		{
			name: "emphasis tag counts",
			body: "*#tag* and **#other**\n",
			want: []string{"tag", "other"},
		},
		{
			name: "numbers count",
			body: "Year #123 and #y1984 count.\n",
			want: []string{"123", "y1984"},
		},
		{
			name: "trailing punctuation stripped",
			body: "See #hugo, #python. (#go!) [#rs?]\n",
			want: []string{"hugo", "python", "go", "rs"},
		},
		{
			name: "nested tag kept whole",
			body: "Status #project/active today.\n",
			want: []string{"project/active"},
		},
		{
			name: "mid-word hash rejected",
			body: "Email foo#bar and C# here.\n",
			want: nil,
		},
		{
			name: "link destination ignored",
			body: "See [setup](setup.md#requirements).\n",
			want: nil,
		},
		{
			name: "link text counts",
			body: "See [#tag](page.md).\n",
			want: []string{"tag"},
		},
		{
			name: "autolink fragment ignored",
			body: "Visit <http://example.com/#frag>.\n",
			want: nil,
		},
		{
			name: "bare url fragment ignored",
			body: "Visit http://example.com/#frag.\n",
			want: nil,
		},
		{
			name: "image alt ignored",
			body: "![#alt](img.png)\n",
			want: nil,
		},
		{
			name: "blockquote counts",
			body: "> #quote\n",
			want: []string{"quote"},
		},
		{
			name: "list text counts",
			body: "- item #one\n- item #two\n",
			want: []string{"one", "two"},
		},
		{
			name: "dedup preserves order",
			body: "#b #a #b #c\n",
			want: []string{"b", "a", "c"},
		},
		{
			name: "case preserved",
			body: "#Go and #go\n",
			want: []string{"Go", "go"},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := extractInlineTags(tt.body); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("extractInlineTags() = %q, want %q", got, tt.want)
			}
		})
	}
}
