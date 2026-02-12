# Feature Specification: Inverted Paragraph Merging & Wrapping

**Feature Branch**: `002-wrap-long-paragraphs`  
**Created**: 2026-02-12  
**Status**: Draft  
**Input**: User description: "Now, we will invert the paragraph merging strategy - do merge the paragraphs. Instead, if the paragraph is longer than paragraph width, wrap the paragraph. -- THIS IS NOT TRUE: Just wrap long lines"

## Clarifications

### Session 2026-02-12

- Q: Should the system merge subsequent lines or just wrap long ones? → A: Wrap Only (No Merging): Process each line independently. If a line is too long, wrap it; otherwise, leave it as is.
- Q: Should wrapped lines preserve the indentation of the original line? → A: Flush Left: All wrapped lines (after the first) start at the left margin (no indentation).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Wrap Long Lines (Priority: P1)

As a researcher, I want my OCR text to have a maximum line width so that long unwrapped lines are hard-wrapped to a specific width for better readability, while preserving existing line breaks for shorter lines.

**Why this priority**: This fulfills the specific requirement to handle long unwrapped paragraphs by breaking them down without forced merging of other text.

**Independent Test**: Provide a markdown file with some lines significantly longer than the typewriter width and some shorter. Verify that only the long lines are wrapped and no existing line breaks between shorter lines are removed.

**Acceptance Scenarios**:

1. **Given** a line shorter than the width, **When** the tool is run, **Then** it MUST remain unchanged.
2. **Given** a line longer than the width, **When** the tool is run, **Then** it MUST be wrapped into multiple lines of at most the specified width.
3. **Given** protected markdown elements (lists, headers), **When** the tool is run, **Then** they MUST NOT be wrapped in a way that breaks their structure.

---

### Edge Cases

- **Paragraph Exactly at Width**: A paragraph whose length is exactly the typewriter width should not have a trailing empty line or unnecessary wrap.
- **Very Long Single Word**: If a single word is longer than the width, it should probably stay on its own line or be handled gracefully (defaulting to industry standard wrapping logic).
- **Mixed Content**: A file containing both short lines and very long lines should all follow the same merge-then-wrap logic.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST process each line of the document independently for wrapping.
- **FR-002**: The system MUST NOT automatically merge subsequent non-empty lines into a single string.
- **FR-003**: The system MUST detect when a line's length (excluding trailing newline) exceeds the `typewriter_width`.
- **FR-004**: The system MUST hard-wrap lines that exceed the `typewriter_width` into multiple lines using standard word-wrap. All lines resulting from a wrap (except possibly the first line of the original text) MUST be flush left (no leading indentation).
- **FR-005**: The system MUST maintain the existing protections for markdown structural elements (prefixes like `-`, `*`, `#`, `>`, `|`) and specifically "ANNEX", "APPENDIX", and page numbering patterns.
- **FR-006**: The system MUST preserve exactly one blank line between existing distinct paragraphs.

### Key Entities

- **Typewriter Width**: The maximum allowed characters per line for body text.
- **Merged Paragraph**: A collection of lines combined into a single logical unit before wrapping.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: No line in the output (excluding protected markdown structures) exceeds the `typewriter_width`.
- **SC-002**: 100% of existing line breaks in the input are preserved if the preceding line was shorter than the width.
- **SC-003**: The word-wrap logic correctly preserves words (no splitting words across lines unless the word itself is longer than the width).
- **SC-004**: Protected structures (ANNEX, Page numbers, etc.) remain identical to their state after the first cleaning pass.
