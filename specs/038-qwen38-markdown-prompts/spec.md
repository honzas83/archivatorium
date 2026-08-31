# Feature Specification: Qwen 3.8 Markdown OCR Profile

**Feature Branch**: `038-qwen38-markdown-prompts`

**Created**: 2026-08-31

**Status**: Draft

**Input**: User description: "Create a new `qwen38` OCR mode with streamlined prompts, high reasoning, Markdown-compatible structure and single-line paragraphs, plain-text typewriter headings without Markdown heading/bold/italic styling, generic de-spacing such as `N A T O   S E C R E T` → `NATO SECRET`, and no inferred curly braces from typewritten source; do not modify standard mode."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Receive Markdown-native OCR output (Priority: P1)

As an archive operator, I want Qwen 3.8 OCR output expressed as clean Markdown so that recognized documents can be stored and processed without repairing HTML or indentation-based layout.

**Why this priority**: Markdown compatibility is the primary output contract. Invalid or ambiguous formatting directly degrades the archival document and downstream processing.

**Independent Test**: Process representative pages containing headings, lists, paragraphs, and tables in Qwen 3.8 mode and verify that the recognized structure uses Markdown constructs, contains no generated HTML markup, and does not use leading indentation as its formatting mechanism.

**Acceptance Scenarios**:

1. **Given** a page with visually identifiable title, section, and subsection headings, **When** it is recognized in Qwen 3.8 mode, **Then** each heading remains plain text on its own line without generated Markdown heading, bold, or italic markers.
2. **Given** a clearly structured table, **When** the page is recognized, **Then** the table is represented as a Markdown pipe table with its visible content and ordering preserved.
3. **Given** content that could be represented with HTML or Markdown, **When** the page is recognized, **Then** the generated structural markup uses Markdown and contains no generated HTML elements.
4. **Given** visually nested content, **When** the page is recognized, **Then** nesting is represented with Markdown constructs rather than global or layout-derived indentation.
5. **Given** any heading, label, table cell, or prose text printed with artificial spacing between characters, such as `N A T O   S E C R E T`, **When** it is recognized, **Then** the output restores normal lettering and word boundaries as `NATO SECRET`.
6. **Given** a typewritten character that could be misrecognized or normalized as a curly brace, **When** it is recognized in Qwen 3.8 mode, **Then** the output does not contain `{` or `}` unless the corresponding brace is unambiguously visible in the source.

---

### User Story 2 - Preserve paragraphs as single lines (Priority: P2)

As an archive operator, I want each recognized prose paragraph emitted as one unwrapped line so that source line wrapping does not create false paragraph boundaries or disrupt later text processing.

**Why this priority**: OCR often reproduces visual line endings that have no semantic meaning. Removing those wraps makes the output stable while retaining true paragraph boundaries.

**Independent Test**: Process a page where one prose paragraph spans several visual lines and a second paragraph is visually separate; verify that each paragraph becomes one unwrapped line and exactly one blank line separates the paragraphs.

**Acceptance Scenarios**:

1. **Given** one prose paragraph wrapped across multiple visual lines, **When** it is recognized, **Then** its text is joined into one non-wrapped output line without changing word order or punctuation.
2. **Given** two visually separate prose paragraphs, **When** they are recognized, **Then** each paragraph occupies one line and one blank line separates them.
3. **Given** a list or table whose row boundaries are meaningful, **When** it is recognized, **Then** the single-line paragraph rule does not collapse distinct list items or table rows.

---

### User Story 3 - Use high reasoning without leaking reasoning text (Priority: P3)

As an archive operator, I want a dedicated Qwen 3.8 OCR mode to use high reasoning so that difficult layout and structure decisions receive the strongest configured analysis while saved output still contains only recognized document content.

**Why this priority**: Stronger reasoning can improve structural interpretation, but it must remain an internal processing aid and must not alter the clean output contract.

**Independent Test**: Inspect a Qwen 3.8 mode request and its saved result; verify that the dedicated prompts and high reasoning are used and that any reasoning preamble returned by the model is absent from the recognized Markdown.

**Acceptance Scenarios**:

1. **Given** Qwen 3.8 mode is selected, **When** a recognition request is made, **Then** the request uses the dedicated Markdown prompts and high reasoning level.
2. **Given** the model returns internal reasoning before recognized content, **When** the response is saved, **Then** only the recognized Markdown remains.
3. **Given** standard, GLM, or FireRed mode is selected, **When** a recognition request is made, **Then** that existing mode retains its current prompt, context, and reasoning behavior.

### Edge Cases

- A page may contain both prose and preformatted material whose line boundaries are meaningful.
- A visually ambiguous table may not support a reliable pipe-table interpretation.
- A document may visibly contain literal HTML-like text that is source content rather than generated structure.
- Headings or list nesting may be visually ambiguous; the output must not invent structure that is not supported by the page.
- A document may use capitalization, spacing, underlining, or position to distinguish headings; those cues must not be converted into Markdown heading, bold, or italic styling.
- A paragraph may contain inline emphasis, links, punctuation, or OCR uncertainty markers that must remain on the same line.
- Genuine standalone letters or symbols may appear near artificially spaced words and must not be merged into unrelated text.
- A model may return reasoning text even when the saved output contract excludes it.
- A typewritten glyph may resemble a curly brace even though the source typewriter did not provide curly braces; ambiguous glyphs must retain source fidelity without being normalized into `{` or `}`.
- A page may be blank, unreadable, or contain only an image with no recognizable text.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The OCR command MUST provide a distinct `qwen38` mode without changing the behavior of any existing mode.
- **FR-002**: Qwen 3.8 mode MUST instruct the selected model to return document content in Markdown rather than generated HTML.
- **FR-003**: Qwen 3.8 mode output MUST keep visually evident headings as plain-text lines while representing visible lists, numbering, tables, and paragraph boundaries with appropriate Markdown constructs.
- **FR-004**: Qwen 3.8 mode output MUST NOT use global leading indentation or reproduced page-layout indentation as the primary formatting mechanism.
- **FR-005**: In Qwen 3.8 mode, every recognized prose paragraph MUST be emitted as one non-wrapped line regardless of visual line wrapping in the source page.
- **FR-006**: In Qwen 3.8 mode, visually separate prose paragraphs MUST be separated by one blank line.
- **FR-007**: The Qwen 3.8 single-line paragraph rule MUST preserve distinct Markdown block boundaries, including headings, list items, table rows, fenced preformatted blocks, and page-level separators.
- **FR-008**: In Qwen 3.8 mode, clearly structured tables MUST be represented as Markdown pipe tables; tables that cannot be represented reliably MUST use a Markdown-compatible preformatted representation without generated HTML.
- **FR-009**: The Qwen 3.8 mode instructions MUST remain concise, direct, non-duplicative, and organized around the required output contract.
- **FR-010**: Qwen 3.8 mode MUST request the high reasoning level.
- **FR-011**: Internal Qwen 3.8 model reasoning MUST remain absent from normalized page text, previous-page context, and saved Markdown.
- **FR-012**: Qwen 3.8 mode output MUST preserve visible text, ordering, punctuation, uncertainty, and supported structure without correction, summarization, or invented content.
- **FR-013**: Standard, GLM, and FireRed modes MUST retain their current prompts, context behavior, reasoning settings, and output contracts.
- **FR-014**: Existing model selection, retries, page ordering, resume behavior, output naming, response cleanup, and timing logs MUST remain unchanged.
- **FR-015**: Qwen 3.8 mode instructions MUST explicitly require artificial typewriter-style inter-character spacing anywhere in recognized text to be collapsed while preserving normal word boundaries, and MUST include `N A T O   S E C R E T` → `NATO SECRET` as the canonical example.
- **FR-016**: Qwen 3.8 mode MUST preserve visually supported headings as plain text on their own lines and MUST NOT generate Markdown heading markers (`#`, `##`, or other levels), bold markers (`**` or `__`), or italic markers (`*` or `_`) from capitalization, spacing, underlining, position, or other typewriter layout cues.
- **FR-017**: Qwen 3.8 mode instructions MUST state that the source typewriter did not provide curly braces, MUST prohibit inferring or normalizing any character into `{` or `}`, and MUST permit either brace only when it is unambiguously visible in the source image.

### Key Entities

- **Qwen 3.8 OCR Profile**: The dedicated `qwen38` mode behavior, including its instructions, high reasoning level, context behavior, and output rules.
- **Recognized Markdown Page**: One page of source-faithful text represented with Markdown blocks and unwrapped prose paragraphs.
- **Prose Paragraph**: A semantically continuous text block whose visual source-line breaks are removed while its words, punctuation, and inline meaning are preserved.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In all validation samples containing headings, lists, paragraphs, or clearly structured tables, headings remain unstyled plain text, other generated structure uses valid Markdown constructs, and no generated HTML elements appear.
- **SC-002**: In all validation samples with prose wrapped across visual lines, each resulting prose paragraph occupies exactly one output line while all true paragraph boundaries remain separated.
- **SC-003**: In all mixed-content validation samples, enforcing single-line paragraphs preserves every distinct heading, list item, table row, and preformatted block boundary.
- **SC-004**: Every inspected `qwen38` request uses its dedicated prompts and high reasoning, while every saved validation output excludes internal reasoning text.
- **SC-005**: Standard, GLM, and FireRed modes and established OCR workflows pass their regression scenarios without changes to requests, saved page order, filenames, resume behavior, or timing visibility.
- **SC-006**: Reviewers can determine the complete Qwen 3.8 mode formatting contract from one concise instruction set without contradictory or duplicated rules.
- **SC-007**: In all validation samples using artificial inter-character spacing, spaced letters are joined into their intended words while genuine word boundaries and standalone symbols remain correct.
- **SC-008**: In all validation samples containing typewriter headings or emphasized-looking text, no generated Markdown heading, bold, or italic markers appear.
- **SC-009**: In all typewritten validation samples without visibly unambiguous curly braces, the recognized output introduces no `{` or `}` characters.

## Assumptions

- `qwen38` is a new value of the existing mode-selection interface. The model identifier continues to be selected independently through the existing model option; changing the default model identifier is outside this feature.
- The new instructions and high reasoning level apply only to Qwen 3.8 mode. Standard, GLM, and FireRed remain unchanged.
- "Pure Markdown" prohibits generated HTML used for document structure. Literal HTML-like text visibly present in the source is preserved safely as content.
- A fixed-width fallback for an ambiguous table or preformatted source is represented as a fenced Markdown block rather than indentation-based or HTML formatting.
- Existing response normalization continues to remove leaked reasoning before content is reused as context or saved.
- Prompt streamlining may change wording and ordering as long as every mandatory output rule remains explicit and testable.
- Artificial typewriter-style spacing may occur anywhere in a page, including generic prose, headings, labels, and table cells. It is visually distinguishable from genuine sequences of standalone one-character tokens; ambiguous cases retain the visible text rather than guessing.
- The typewriters used for the target documents did not provide curly braces. A brace visibly introduced by another process or present in non-typewritten source content may be transcribed only when its shape is unambiguous.
- Plain text is valid Markdown-compatible output. Qwen 3.8 may still use Markdown for visible lists, pipe tables, and fenced literal blocks, but not to style headings or add bold/italic emphasis.
