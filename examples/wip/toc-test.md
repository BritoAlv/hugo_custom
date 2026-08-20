# TOC stress test

A large page used to exercise the right TOC rail: deep nesting, many
sections, and enough content to scroll both the page and the rail itself.

## Section 01 — Introduction

Some text to make the page long enough to scroll. Lorem ipsum dolor sit
amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut
labore et dolore magna aliqua.

### 01.1 What is this page?

Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
aliquip ex ea commodo consequat.

#### 01.1.1 Nested heading level 4

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum
dolore eu fugiat nulla pariatur.

#### 01.1.2 Another level 4

Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia
deserunt mollit anim id est laborum.

### 01.2 Goals

- Exercise the scrollspy with many headings
- Force the rail's own scrollbar
- Verify nested connector lines and guide lines
- Check the active link follows the reading position

## Section 02 — Deep nesting

### 02.1 First level

#### 02.1.1 Second level

##### 02.1.1.1 Third level

###### 02.1.1.1.1 Fourth level

Sed ut perspiciatis unde omnis iste natus error sit voluptatem
accusantium doloremque laudantium, totam rem aperiam.

### 02.2 Second branch

#### 02.2.1 Nested item

##### 02.2.1.1 Deeper still

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua.

#### 02.2.2 Sibling item

Ut enim ad minim veniam, quis nostrud exercitation ullamco.

### 02.3 Third branch

#### 02.3.1 Nested

#### 02.3.2 Nested

## Section 03 — Long scroll area

This section repeats content so the page becomes long enough that the rail
needs its own internal scrolling.

### 03.1 Paragraph block A

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
commodo consequat. Duis aute irure dolor in reprehenderit in voluptate
velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat
cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id
est laborum.

#### 03.1.1 Detail

More filler text to push the headings apart. Sed ut perspiciatis unde
omnis iste natus error sit voluptatem accusantium doloremque laudantium.

### 03.2 Paragraph block B

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
commodo consequat. Duis aute irure dolor in reprehenderit in voluptate
velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat
cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id
est laborum.

#### 03.2.1 Detail

More filler text to push the headings apart. Sed ut perspiciatis unde
omnis iste natus error sit voluptatem accusantium doloremque laudantium.

### 03.3 Paragraph block C

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
commodo consequat. Duis aute irure dolor in reprehenderit in voluptate
velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat
cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id
est laborum.

#### 03.3.1 Detail

More filler text to push the headings apart. Sed ut perspiciatis unde
omnis iste natus error sit voluptatem accusantium doloremque laudantium.

## Section 04 — Code blocks

Code blocks should not disturb the headings or the TOC.

### 04.1 Python

```python
def toc_test(headings: list[str]) -> None:
    for i, h in enumerate(headings):
        print(f"{i}: {h}")
```

### 04.2 Shell

```sh
uv run hugo-custom --preview
```

#### 04.2.1 Why?

To verify the scrollspy with a heading that follows a code block.

## Section 05 — Even more content

### 05.1 Block one

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua.

### 05.2 Block two

Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.

#### 05.2.1 Sub detail

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum.

#### 05.2.2 Sub detail

Excepteur sint occaecat cupidatat non proident.

### 05.3 Block three

Sunt in culpa qui officia deserunt mollit anim id est laborum.

## Section 06 — Anchors and links

### 06.1 Link to a heading

Jump to [Section 03](#section-03--long-scroll-area) from here.

### 06.2 Link to a nested heading

Jump to [05.2 Block two](#052-block-two) from here.

## Section 07 — Final section

Last stretch of content. Lorem ipsum dolor sit amet, consectetur
adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore
magna aliqua.

### 07.1 Nested final

Ut enim ad minim veniam, quis nostrud exercitation ullamco.

#### 07.1.1 Deep final

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum
dolore eu fugiat nulla pariatur.

### 07.2 Another nested final

Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia
deserunt mollit anim id est laborum.

## Section 08 — One more

### 08.1 Nested

### 08.2 Nested

#### 08.2.1 Deep

##### 08.2.1.1 Deeper

###### 08.2.1.1.1 Deepest

The end. Check that the rail scrolls internally and the last heading can
be reached in the TOC.