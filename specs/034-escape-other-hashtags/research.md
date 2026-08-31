# Research: Escaping Non-Standard Hashtags and Simplifying Index Pages

This document outlines the technical research, selected approach, and alternatives considered for implementing feature `034-escape-other-hashtags`.

## Escaping Non-Standard Hashtags

### The Problem
Historical documents in the NATO archive contain administrative markings like `DOCUMENT DESTRUCTION MEMO. #67-87155`. Because Obsidian treats any `#` followed by non-numeric characters (like hyphens `-` or slashes `/`) as tags, these clutter the tag list in the Obsidian vault.

### Selected Approach: Procedural String Index Finder
A clean, line-by-line index-based search using Python's C-optimized `.find()` is used to selectively prefix non-standard hashtags with a backslash `\`.
By tracking the fenced code block state (`in_code_block`) across lines and utilizing high-performance string methods on each line, we can dynamically detect and protect:
* Fenced code blocks (line-level check)
* Inline code blocks (using C-optimized `.count("`", 0, idx) % 2 != 0` check)
* Markdown headers (including blockquote-prefixed ones)
* Pre-existing escaped hashes (`\#` check via index lookbehind `line[idx-1] == "\\"`)
* Canonical Obsidian tags (`#Entities/`, `#Topics/`, `#Tags/` via `line.startswith()`)

Any other `#` followed by a non-whitespace character is safely escaped.

#### Finder Logic Outline
1. Split the text into lines.
2. For each line:
   * If starting/ending a code block (starts with ```` ``` ````), toggle state and skip processing.
   * If inside a code block, skip processing.
   * If the line is a markdown header (starts with `#` with optional preceding `>`), skip processing.
   * Run a loop using `line.find("#", start_pos)` to skip scanning and jump directly to each hash:
     - Check if it is already escaped (`line[idx - 1] == "\\"`).
     - Check if it lies inside inline code via even/odd backtick count before `idx`.
     - Check if it starts a canonical tag via `line.startswith()`.
     - Escape the `#` character using string slicing if followed by a non-whitespace character.

### Alternatives Considered
1. **Single Large Regular Expression**:
   * *Rejected*: Although a single regex pattern using group protections works, it is harder to maintain, less readable, and more complex to extend safely when handling overlapping edge cases (like nested blockquote headers).
2. **Full AST Markdown Parser (e.g. `mistletoe`, `markdown-it-py`)**:
   * *Rejected*: Adding external python markdown parsing libraries increases dependency size and incurs substantial parsing overhead over a large 30k document vault.
3. **Simple String Replacement**:
   * *Rejected*: Replacing all `#` characters with `\#` would destroy actual markdown headers (`# Header`), code blocks, and legitimate tags.

---

## Simplifying Index Pages

### The Problem
Generating indices that link to all matching documents for a 30,000 document vault results in files (like `Index - Tags.md` or `Index - Organizations.md`) with hundreds of thousands of lines. This causes Obsidian to lag or crash.

### Selected Approach: Hybrid Capped Listing with Search URLs
Limit the inline document links under each tag/entity to **50**.
* If a tag has $\le 50$ documents, list them all inline.
* If a tag has $> 50$ documents:
  1. List the first 50.
  2. Show a line stating the remaining count (e.g. `... and 142 more.`).
  3. Provide an Obsidian Search URI pointing to that tag query:
     `obsidian://search?vault=VAULT_NAME&query=tag:%23Tags/DefencePolicy` (url-encoded).

This leverages Obsidian's extremely fast native search engine rather than trying to display massive lists inside a single note.

### Alternatives Considered
1. **Alphabetical/Prefix Splitting (e.g. `Index - Tags - A-M.md`)**:
   * *Rejected*: Some letters/prefixes still contain a disproportionately large number of matches, which doesn't guarantee the note size stays within Obsidian's performance limits.
2. **Subfolder note per tag (e.g. `Indices/Tags/DefencePolicy.md`)**:
   * *Rejected*: Creates thousands of files in the workspace, adding filesystem overhead without solving the size issue for extremely frequent tags (which can still have thousands of matching documents).

---

## Speed Optimization Design Decisions

1. **Module-Level Regex Pre-Compilation**:
   Compiling a complex regex pattern (which checks for code blocks, tags, and blockquote headers) on every document check would consume significant CPU time over 30,000 documents. Pre-compiling it to `HASHTAG_ESCAPE_PATTERN` at module load time avoids compilation overhead.
2. **Fast-path String Scanning**:
   Executing regex matching is significantly slower than simple substring search. By checking `if "#" not in text: return text` first, we bypass the regex engine completely for the vast majority of lines/documents that contain no hash characters, resulting in a substantial speedup.
