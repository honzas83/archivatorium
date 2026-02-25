# Feature Specification: DOCX Generation with Page Mirroring

**Feature Branch**: `005-docx-generation`  
**Created**: 2026-02-25  
**Status**: Draft  
**Input**: User description: "Add a commandline flag, that turns on DOCX generation. Requirements: DOCX must have the same number of pages like the original. Use --- and # Page X markers Format one page of MD to one page in DOCX Use fixed-width font other than Courier New"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate DOCX with Page Mirroring (Priority: P1)

As a researcher or archivist, I want to convert my processed OCR Markdown files into DOCX format while preserving the original page boundaries, so that the digital document mirrors the physical page structure.

**Why this priority**: This is the core functional requirement. It ensures the output format meets the specific layout needs of the user.

**Independent Test**: Can be tested by running the CLI with the DOCX flag on a Markdown file containing `---` and `# Page X` markers and verifying the resulting DOCX has the correct number of pages and content distribution.

**Acceptance Scenarios**:

1. **Given** a Markdown file with 3 pages separated by `---` and `# Page X` markers, **When** the CLI is run with the `--docx` flag, **Then** a DOCX file is created with exactly 3 pages.
2. **Given** a Markdown file, **When** the CLI is run with the `--docx` flag, **Then** the text in the DOCX is rendered in a fixed-width font that is not Courier New (e.g., Consolas, Roboto Mono, or similar).

---

### User Story 2 - Optional DOCX Generation (Priority: P2)

As a user, I want to choose whether or not to generate a DOCX file using a command-line flag, so that I don't create unnecessary files when I only need Markdown.

**Why this priority**: Essential for CLI usability and preventing unwanted side effects.

**Independent Test**: Run the tool without the flag and verify no DOCX is created; run with the flag and verify it is.

**Acceptance Scenarios**:

1. **Given** the CLI is run without the DOCX flag, **When** processing completes, **Then** no DOCX file should be present in the output directory.
2. **Given** the CLI is run with the DOCX flag, **When** processing completes, **Then** a DOCX file should be present in the output directory alongside the Markdown output.

---

### Edge Cases

- **Empty Pages**: What happens when there are two page markers in a row with no text between them? (Assumption: Create a blank page in DOCX).
- **Missing Page Markers**: How does the system handle Markdown files that don't use the standard `---` / `# Page X` markers? (Assumption: Treat the entire file as a single page).
- **Large Content**: What if the text for a single "page" in Markdown exceeds what can fit on one physical DOCX page? (Assumption: The text should be shrunk or overflow should be handled gracefully, but the requirement "Format one page of MD to one page in DOCX" implies we should force a page break after each MD page).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a command-line flag (e.g., `--docx`) to enable DOCX generation.
- **FR-002**: The system MUST detect page boundaries in Markdown using `---` and `# Page X` markers.
- **FR-003**: The system MUST ensure the output DOCX has a 1:1 mapping between Markdown sections (separated by markers) and DOCX pages.
- **FR-004**: The system MUST use a fixed-width font for all text in the DOCX.
- **FR-005**: The fixed-width font MUST NOT be "Courier New".
- **FR-006**: The system MUST place the generated DOCX file in the same output directory as the processed Markdown file, using the same base filename.

### Key Entities *(include if feature involves data)*

- **Markdown Page**: A segment of text bounded by `---` and `# Page X` markers.
- **DOCX Document**: The output file containing the formatted pages.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of Markdown files processed with the DOCX flag produce a valid DOCX file.
- **SC-002**: The page count of the generated DOCX exactly matches the number of `# Page X` markers found in the source Markdown.
- **SC-003**: Visual inspection confirms that 100% of the text in the DOCX uses a non-Courier fixed-width font.
- **SC-004**: DOCX generation adds less than 20% overhead to the total processing time per file.
