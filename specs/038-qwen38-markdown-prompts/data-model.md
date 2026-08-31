# Phase 1 Data Model: Qwen 3.8 Markdown OCR Profile

This feature changes transient request configuration and recognized text contracts. It introduces no persisted schema or storage entity.

## Qwen 3.8 OCR Profile

Immutable behavior selected by the new `qwen38` OCR mode.

| Field | Type | Validation | Feature value |
|-------|------|------------|---------------|
| `name` | non-empty mode identifier | Must resolve through the existing mode selector | `qwen38` |
| `system_prompt` | text | Must contain the complete, non-contradictory output contract | Streamlined Markdown transcription contract |
| `user_prompt` | text | Must be a concise current-page instruction | One sentence referencing the output contract |
| `include_previous_page_context` | boolean | Existing mode behavior remains unchanged | `true` |
| `inference_defaults` | name/value pairs | Uses the established general OCR output-token default | Existing standard output-token value |
| `think` | boolean, named reasoning level, or absent | Named level is one of `low`, `medium`, `high` | `high` |

### Mode isolation

| Mode | Prompt behavior | Previous-page context | Reasoning field |
|------|-----------------|-----------------------|-----------------|
| Standard | Existing standard prompts | Existing behavior retained | Absent |
| Qwen 3.8 | New Markdown contract | Included when available | `high` |
| GLM | Existing recognition prompt | Excluded | Explicit `false` |
| FireRed | Existing FireRed prompt | Excluded | Absent |

## Qwen 3.8 Prompt Contract

Rules governing the model's recognized page output.

| Rule | Validation |
|------|------------|
| Output scope | Contains transcription only; no commentary, summary, correction, inference, or invented content. |
| Heading hierarchy | Uses `#`, `##`, `###`, and subsequent ATX levels for visually supported hierarchy; ordinary prose remains unmarked. |
| Structure | Uses Markdown lists, tables, breaks, notes, and captions; generated HTML is prohibited. |
| Top-level alignment | Top-level blocks begin at column one; page margins and layout indentation are not reproduced. |
| Markdown whitespace | Indentation is permitted only when Markdown syntax requires nesting or within a fenced literal block. |
| Prose paragraphs | Every prose paragraph occupies one physical line; visual wraps are joined; distinct paragraphs have one blank line between them. |
| Tables | Clear structures use pipe tables; ambiguous or fixed-width structures use fenced plain text. |
| Artificial letter spacing | Inter-character spacing anywhere in headings, prose, labels, or table cells is collapsed semantically while intended word boundaries remain; canonical example is `N A T O   S E C R E T` → `NATO SECRET`. |
| Curly-brace fidelity | Characters are never inferred or normalized into `{` or `}`; a brace is output only when unambiguously visible in the current image. |
| Fidelity | Visible wording, capitalization, punctuation, typos, numbering, meaningful whitespace, and reading order are preserved. |
| Unreadable/blank content | Illegible text becomes `[unreadable]`; empty output is reserved for a truly blank page. |
| Previous-page context | Context is not copied unless the same text is visible on the current page. |

## OCR Chat Request

Transient request sent for one Qwen 3.8 mode page.

| Field | Feature behavior |
|-------|------------------|
| Model | Exact operator-selected identifier; no Qwen-specific rewriting and no default change. |
| Messages | System prompt contract followed by the concise user prompt, image, and optional previous-page context. |
| Reasoning | Named high level. |
| Options | Existing context length, general output-token default, and explicit CLI overrides remain unchanged. |
| Streaming | Existing non-streaming behavior remains unchanged. |

## Recognized Markdown Page

Normalized page content used for output and optional subsequent-page context.

| Property | Validation |
|----------|------------|
| Reasoning-free | Separate reasoning is ignored and inline content through the final exact closing reasoning marker is removed. |
| Markdown-native | Generated structure contains Markdown rather than HTML. |
| Heading hierarchy | Supported title, section, and subsection levels use consistent ATX markers; prose is not promoted. |
| Paragraph shape | Prose paragraphs are unwrapped single lines; other Markdown blocks retain their required boundaries. |
| Alignment | No shared artificial top-level indentation remains. |
| Letter spacing | Artificially spaced lettering is rendered as intended words with normal word boundaries. |
| Curly braces | Typewritten glyphs are not normalized into `{` or `}` unless a brace is unambiguously visible. |
| Source fidelity | No correction, summary, paraphrase, or unsupported structure is introduced. |

## Relationships and State Flow

1. The selected mode resolves to exactly one immutable OCR profile.
2. Qwen 3.8 mode combines its dedicated prompts, current image, optional normalized previous-page context, model identifier, options, and high reasoning into one request.
3. A successful response exposes recognized content and may expose reasoning separately or inline.
4. Existing normalization removes inline reasoning leakage and shared global indentation.
5. The normalized Markdown page is saved and may become context for the next Qwen 3.8 mode page.

No new persistent states, migrations, or lifecycle transitions are introduced.
