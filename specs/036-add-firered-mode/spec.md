# Feature Specification: Add FireRed OCR Mode

**Feature Branch**: `036-add-firered-mode`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Add a new mode firered for the FireRed OCR model, this model will use the following prompt and no previous-page-context."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Recognize documents with the FireRed profile (Priority: P1)

As a user processing PDF pages with a FireRed OCR model, I want to explicitly select the FireRed mode so that every page receives the model's prescribed transcription instructions.

**Why this priority**: The dedicated prompt is the core value of the mode and allows users to obtain FireRed-oriented OCR without changing the normal OCR workflow.

**Independent Test**: Process a single-page document with `--mode firered` and verify that its recognition request uses the exact supplied prompt and the resulting transcription is retained in the usual output.

**Acceptance Scenarios**:

1. **Given** a valid PDF page, **When** the user runs OCR with `--mode firered`, **Then** the page recognition request uses the exact FireRed prompt defined in FR-003.
2. **Given** a FireRed-mode request, **When** the model returns a transcription, **Then** the transcription is stored in the normal document output and reading order.

---

### User Story 2 - Keep FireRed pages independent (Priority: P1)

As a user processing a multipage or resumed document, I want each FireRed page to be recognized without text from another page so that recognition is based only on the page image and FireRed instructions.

**Why this priority**: Page isolation is explicitly required for this model profile and must hold in normal and recovery processing.

**Independent Test**: Recognize a multipage document and resume a partially recognized document in FireRed mode; inspect every new request to confirm that it contains no recognized text or textual context from another page.

**Acceptance Scenarios**:

1. **Given** a multipage document whose previous page has been recognized, **When** the next page is recognized in FireRed mode, **Then** the request contains no text or textual context from the previous page.
2. **Given** a partially recognized FireRed-mode document with a missing page, **When** processing resumes, **Then** the recovered page is recognized without text or textual context from any neighboring page.
3. **Given** a FireRed-mode recognition that is retried, **When** the retry is sent, **Then** it remains independent of all other page transcriptions.

---

### User Story 3 - Preserve existing OCR modes (Priority: P1)

As an existing user, I want the new FireRed option to be opt-in so that normal and GLM OCR workflows continue to use their established behavior.

**Why this priority**: Existing batch jobs must not change merely because another mode becomes available.

**Independent Test**: Run representative OCR commands with the mode omitted, with `--mode standard`, and with `--mode glm`; verify their prompts and page-context behavior match their pre-FireRed behavior.

**Acceptance Scenarios**:

1. **Given** an existing OCR invocation without a mode option, **When** it is run after FireRed mode is introduced, **Then** it retains standard-mode prompting and previous-page context behavior.
2. **Given** an OCR invocation with `--mode glm`, **When** it is run after FireRed mode is introduced, **Then** it retains GLM-mode prompting and independent-page behavior.
3. **Given** an unsupported mode value, **When** the user starts OCR, **Then** the command rejects it clearly before recognizing any page.

### Edge Cases

- A single-page document in FireRed mode is recognized with the FireRed prompt and without any page-derived textual context.
- The first page, a missing page, and a retry in FireRed mode must not receive text from a previous, next, or any other page.
- Empty or failed recognition output may follow the existing recovery behavior, but every FireRed-mode retry must use the FireRed prompt and remain page-independent.
- Selecting FireRed mode must not change input discovery, output naming, page ordering, resume detection, or output structure.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The OCR command MUST accept an explicitly selected FireRed mode through `archivatorium ocr <input> --mode firered`.
- **FR-002**: The command MUST accept `firered` in addition to the existing supported OCR mode values and MUST reject unsupported mode values with a clear error before recognizing any page.
- **FR-003**: Every page recognition request in FireRed mode MUST use exactly this prompt:

  ```text
  You are an expert in converting PDF images to Markdown format.

  Please convert the provided document image into Markdown while preserving the original document structure.

  Requirements:
  - Preserve headings, paragraphs, lists, and reading order.
  - Convert tables to HTML table format.
  - Convert mathematical formulas to LaTeX.
  - Ignore figures and images.
  - Do not add, summarize, correct, or infer any content that is not present in the document.
  - Output only the converted Markdown.
  ```
- **FR-004**: In FireRed mode, every page MUST be recognized independently; the recognition request MUST NOT include recognized text or textual context derived from a previous, next, or other page.
- **FR-005**: FR-003 and FR-004 MUST apply to initial processing, resumed processing, missing-page recovery, and retries.
- **FR-006**: Selecting FireRed mode MUST retain existing OCR behavior outside the mode-specific differences in FR-003 through FR-005, including model selection, inference settings, input discovery, output formatting, page ordering, retry handling, and resume validation.
- **FR-007**: Omitting `--mode`, explicitly selecting `--mode standard`, or explicitly selecting `--mode glm` MUST preserve the pre-existing behavior of the respective mode.

### Key Entities

- **OCR Mode Profile**: The explicitly selected recognition behavior for a run. It determines the prompt and page-context policy but does not replace the user's model selection or alter unrelated OCR behavior.
- **Page Recognition Request**: One page image combined with its selected mode's prompt and applicable recognition settings. In FireRed mode it contains no textual context derived from another page.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In single-page, multipage, resumed, missing-page recovery, and retry validation, 100% of FireRed-mode recognition requests use the exact prompt in FR-003.
- **SC-002**: In the same validation scenarios, 100% of FireRed-mode recognition requests contain no recognized text or textual context derived from another page.
- **SC-003**: In FireRed-mode acceptance testing, 100% of returned transcriptions retain their existing page order and output structure.
- **SC-004**: All representative standard-mode and GLM-mode acceptance scenarios pass unchanged after FireRed mode is added.
- **SC-005**: A user can activate the FireRed profile by adding only `--mode firered` to an existing OCR command.

## Assumptions

- FireRed mode is opt-in; standard mode remains the default when the mode option is omitted.
- The selected OCR model remains an independent user choice; FireRed mode supplies the FireRed prompt and page-context policy without selecting or replacing a model.
- Existing inference defaults and explicit inference overrides continue to apply in FireRed mode because no FireRed-specific values were supplied.
- “No previous-page-context” includes direct prior-page text and every prompt fragment derived from another page's recognized text.
- The existing OCR pipeline continues to manage rendering, output assembly, resume validation, retry decisions, and error reporting.
