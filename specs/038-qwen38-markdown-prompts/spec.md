# Feature Specification: Qwen 3.8 Markdown OCR Profile

**Feature Branch**: `038-qwen38-markdown-prompts`

**Created**: 2026-08-31

**Status**: Draft

**Input**: User description: "Create a Qwen 3.8 OCR configuration with streamlined prompts, high reasoning, mandatory Markdown output, and mandatory single-line paragraphs."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Receive Markdown-native OCR output (Priority: P1)

As an archive operator, I want Qwen 3.8 OCR output expressed as clean Markdown so that recognized documents can be stored and processed without repairing HTML or indentation-based layout.

**Why this priority**: Markdown compatibility is the primary output contract. Invalid or ambiguous formatting directly degrades the archival document and downstream processing.

**Independent Test**: Process representative pages containing headings, lists, paragraphs, and tables in standard OCR mode and verify that the recognized structure uses Markdown constructs, contains no generated HTML markup, and does not use leading indentation as its formatting mechanism.

**Acceptance Scenarios**:

1. **Given** a page with visually identifiable headings, paragraphs, and lists, **When** Qwen 3.8 recognizes the page in standard mode, **Then** the output represents those elements with valid Markdown structure.
2. **Given** a clearly structured table, **When** the page is recognized, **Then** the table is represented as a Markdown pipe table with its visible content and ordering preserved.
3. **Given** content that could be represented with HTML or Markdown, **When** the page is recognized, **Then** the generated structural markup uses Markdown and contains no generated HTML elements.
4. **Given** visually nested content, **When** the page is recognized, **Then** nesting is represented with Markdown constructs rather than global or layout-derived indentation.

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

As an archive operator, I want the standard Qwen 3.8 OCR profile to use high reasoning so that difficult layout and structure decisions receive the strongest configured analysis while saved output still contains only recognized document content.

**Why this priority**: Stronger reasoning can improve structural interpretation, but it must remain an internal processing aid and must not alter the clean output contract.

**Independent Test**: Inspect a standard-mode Qwen 3.8 request and its saved result; verify that high reasoning is requested and that any reasoning preamble returned by the model is absent from the recognized Markdown.

**Acceptance Scenarios**:

1. **Given** Qwen 3.8 is selected in standard OCR mode, **When** a recognition request is made, **Then** the request uses the high reasoning level.
2. **Given** the model returns internal reasoning before recognized content, **When** the response is saved, **Then** only the recognized Markdown remains.
3. **Given** an existing specialized OCR mode is selected, **When** a recognition request is made, **Then** that mode retains its existing prompt, context, and reasoning behavior.

### Edge Cases

- A page may contain both prose and preformatted material whose line boundaries are meaningful.
- A visually ambiguous table may not support a reliable pipe-table interpretation.
- A document may visibly contain literal HTML-like text that is source content rather than generated structure.
- Headings or list nesting may be visually ambiguous; the output must not invent structure that is not supported by the page.
- A paragraph may contain inline emphasis, links, punctuation, or OCR uncertainty markers that must remain on the same line.
- A model may return reasoning text even when the saved output contract excludes it.
- A page may be blank, unreadable, or contain only an image with no recognizable text.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Standard OCR mode MUST instruct the selected Qwen 3.8 model to return document content in Markdown.
- **FR-002**: Generated structural markup in standard-mode output MUST use Markdown rather than HTML.
- **FR-003**: Standard-mode output MUST represent visually evident headings, lists, numbering, tables, and paragraph boundaries with appropriate Markdown constructs.
- **FR-004**: Standard-mode output MUST NOT use global leading indentation or reproduced page-layout indentation as the primary formatting mechanism.
- **FR-005**: Every recognized prose paragraph MUST be emitted as one non-wrapped line regardless of visual line wrapping in the source page.
- **FR-006**: Visually separate prose paragraphs MUST be separated by one blank line.
- **FR-007**: The single-line paragraph rule MUST preserve distinct Markdown block boundaries, including headings, list items, table rows, fenced preformatted blocks, and page-level separators.
- **FR-008**: Clearly structured tables MUST be represented as Markdown pipe tables; tables that cannot be represented reliably MUST use a Markdown-compatible preformatted representation without generated HTML.
- **FR-009**: The OCR instructions MUST remain concise, direct, non-duplicative, and organized around the required output contract.
- **FR-010**: The standard Qwen 3.8 OCR profile MUST request the high reasoning level.
- **FR-011**: Internal model reasoning MUST remain absent from normalized page text, previous-page context, and saved Markdown.
- **FR-012**: The output MUST preserve visible text, ordering, punctuation, uncertainty, and supported structure without correction, summarization, or invented content.
- **FR-013**: Existing specialized OCR modes MUST retain their current prompts, context behavior, reasoning settings, and output contracts.
- **FR-014**: Existing model selection, retries, page ordering, resume behavior, output naming, response cleanup, and timing logs MUST remain unchanged.

### Key Entities

- **Standard OCR Profile**: The recognition behavior used for general OCR, including its instructions, reasoning level, context behavior, and output rules.
- **Recognized Markdown Page**: One page of source-faithful text represented with Markdown blocks and unwrapped prose paragraphs.
- **Prose Paragraph**: A semantically continuous text block whose visual source-line breaks are removed while its words, punctuation, and inline meaning are preserved.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In all validation samples containing headings, lists, paragraphs, or clearly structured tables, the recognized output uses valid Markdown constructs and contains no generated HTML elements.
- **SC-002**: In all validation samples with prose wrapped across visual lines, each resulting prose paragraph occupies exactly one output line while all true paragraph boundaries remain separated.
- **SC-003**: In all mixed-content validation samples, enforcing single-line paragraphs preserves every distinct heading, list item, table row, and preformatted block boundary.
- **SC-004**: Every inspected standard-mode Qwen 3.8 request uses high reasoning, while every saved validation output excludes internal reasoning text.
- **SC-005**: Existing specialized OCR modes and established OCR workflows pass their regression scenarios without changes to requests, saved page order, filenames, resume behavior, or timing visibility.
- **SC-006**: Reviewers can determine the complete standard-mode formatting contract from one concise instruction set without contradictory or duplicated rules.

## Assumptions

- Qwen 3.8 continues to be selected through the existing model-selection interface; changing the default model identifier is outside this feature.
- The new instructions and high reasoning level apply to standard OCR mode. Existing specialized modes remain unchanged.
- "Pure Markdown" prohibits generated HTML used for document structure. Literal HTML-like text visibly present in the source is preserved safely as content.
- A fixed-width fallback for an ambiguous table or preformatted source is represented as a fenced Markdown block rather than indentation-based or HTML formatting.
- Existing response normalization continues to remove leaked reasoning before content is reused as context or saved.
- Prompt streamlining may change wording and ordering as long as every mandatory output rule remains explicit and testable.
