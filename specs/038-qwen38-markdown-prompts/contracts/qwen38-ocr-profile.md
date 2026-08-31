# Qwen 3.8 OCR Prompt and Request Contract

## CLI compatibility

```text
archivatorium ocr [OPTIONS] INPUT_DIR OUTPUT_DIR
```

This feature adds `qwen38` to the existing mode option. The Qwen 3.8 model identifier is supplied independently through the existing model option. No positional argument, default-model change, or output-file change is introduced.

## Exact Qwen 3.8 system prompt

The Qwen 3.8 mode system message is:

```text
You are a precise OCR transcription system. Transcribe only content visible in the current document image, in reading order. Return only the Markdown transcription; do not add commentary or generated HTML.

Output contract:
1. Preserve visible wording, capitalization, punctuation, typos, headings, paragraphs, lists, numbering, tables, footnotes, annotations, section breaks, and legible figure captions. Do not summarize, correct, rephrase, infer, or invent content.
2. Keep visually supported headings as plain text on their own lines. Do not generate Markdown heading markers (#, ##, or other levels), bold (** or __), or italic (* or _) emphasis. Typewritten text has no Markdown styling; do not infer styling from capitalization, spacing, underlining, or position. Use explicit Markdown markers only for visible lists.
3. Put each prose paragraph on one physical line by removing visual line wraps. Separate distinct prose paragraphs with exactly one blank line. Keep plain-text headings, list items, table rows, and fenced-block lines as separate Markdown blocks.
4. Use a Markdown pipe table when the table structure is clear. Otherwise preserve it in a fenced plain-text block. Never generate HTML.
5. Start every top-level block at column 1; do not reproduce page margins or layout indentation. Use indentation only where Markdown syntax requires nested list structure or inside a fenced literal block.
6. IMPORTANT: In any text, collapse artificial typewriter-style spacing between letters while preserving word boundaries. Apply this to headings, prose, labels, and table cells. Example: N A T O   S E C R E T → NATO SECRET.
7. Typewriters used for these documents do not have curly braces. Never infer or normalize characters into { or }. Output a curly brace only when it is unambiguously visible in the current image.
8. Preserve meaningful whitespace inside literal content and write [unreadable] for illegible text. Return an empty transcription only when the page is truly blank.
9. Previous-page text, when supplied, is context only. Never copy it unless the same text is visible in the current image.
```

The artificial-spacing rule is semantic. It does not authorize blindly merging genuine standalone letters, initials, formula symbols, list labels, or other separate tokens. When spacing is visually ambiguous, source fidelity takes precedence over guessing.

The curly-brace rule prevents typewritten glyphs from being normalized into characters unavailable on the source typewriter. Literal `{` or `}` remains valid only when the corresponding brace is unambiguously visible in the current image.

## Exact Qwen 3.8 user prompt

```text
Transcribe this document image according to the output contract. Return only the Markdown transcription.
```

When previous-page context is available, the existing context suffix remains appended after this prompt. The system-level context rule prevents accidental copying.

## Qwen 3.8 request shape

For `qwen38` mode, the outgoing request retains the selected model, existing request assembly, options, image, and non-streaming behavior and uses the named high reasoning level:

```text
model: <exact operator-selected model identifier>
messages:
  - role: system
    content: <exact system prompt above>
  - role: user
    content: <exact user prompt plus optional existing previous-page context suffix>
    images: [<current page image>]
options:
  num_ctx: <existing call value>
  num_predict: <general OCR default or explicit override>
  ...: <existing explicit inference overrides>
stream: false
think: high
```

Retries MUST reuse an identical request.

## Mode isolation matrix

| Behavior | Standard | Qwen 3.8 | GLM | FireRed |
|----------|----------|----------|-----|---------|
| Prompt contract | Existing, unchanged | New Markdown contract | Existing, unchanged | Existing, unchanged |
| Previous-page context | Existing behavior retained | Included when available | Excluded | Excluded |
| Reasoning field | Omitted | `high` | Explicit `false` | Omitted |
| Existing inference defaults | Retained | General OCR defaults retained | Retained | Retained |
| Response normalization | Retained | Retained | Retained | Retained |

## Output examples

Typewriter heading without generated styling:

```text
Source heading: NATO SECRET
Required output: NATO SECRET
Forbidden output: # NATO SECRET or **NATO SECRET**
```

Artificial letter spacing in any kind of text:

```text
Source-like OCR tendency: N A T O   S E C R E T
Required Markdown text:  NATO SECRET
```

Wrapped prose and paragraph boundary:

```text
This is one prose paragraph joined onto one physical line even when the source image wraps it visually.

This is the next visually distinct paragraph.
```

The paragraph rule does not join headings, separate list items, pipe-table rows, or lines inside a fenced literal block.

Ambiguous typewritten glyphs:

```text
Source: no unambiguous curly brace is visible
Required output: do not invent { or }
```

## Compatibility guarantees

- Model selection, default model, context length, explicit inference overrides, retry count, and backoff remain unchanged.
- Standard, GLM, and FireRed prompts and request shapes remain unchanged.
- Recursive discovery, rendering, page ordering, resume skips, output names, headers, response cleanup, and timing logs remain unchanged.
- Internal reasoning never enters saved Markdown or subsequent-page context.
- No heuristic output pass is added to join paragraphs or remove character spacing; the model request owns these semantic formatting decisions.
