# Feature Specification: OCR Post-Processing

**Feature Branch**: `001-ocr-post-processing`  
**Created**: 2026-02-12  
**Status**: Draft  
**Input**: User description: "We will create a project for post-processing LLM-OCR output The ocrpolish will take an input directory, search for *.md files and generate output directory structure with the postprocessed files. First version of cleaning would be automatically detect headers / footers, since those headers footers repeat multiple times in a single file and also among multiple files. You can take a sample of data from @data/sample.txt The script also should automatically infer, if the texts on two subsequent lines are different paragraphs or a continuation of the previous paragraph. If it is a new paragraph, insert an empty line before the paragraph"

## Clarifications

### Session 2026-02-12

- Q: What is the criteria/threshold for a text block to be considered a header or footer? → A: Majority (50%+): Remove lines appearing in more than half of the files.
- Q: Should the system handle markdown-specific elements like lists, tables, or blockquotes differently during paragraph merging? → A: Protect Markdown: Only merge lines if they do not start with markdown symbols (-, *, #, |, >).
- Q: How should existing files in the output directory be handled? → A: Overwrite: Replace existing files in the output directory without prompt.
- Q: How should files with different extensions be handled? → A: Ignore non-matching files; provide CLI option for input mask (e.g., *.md).
- Q: What is the preferred strategy for statistical detection of headers/footers? → A: Streaming: Use two passes: first to count frequencies globally, second to clean.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Clean OCR Text (Priority: P1)

As a researcher, I want to clean my OCR-processed markdown files so that I can read the actual content without distracting headers, footers, and broken paragraphs.

**Why this priority**: This is the core value of the tool. Without this, the OCR output remains difficult to use and analyze.

**Independent Test**: Can be tested by providing a set of markdown files with known repeating headers and broken paragraphs and verifying the output is clean and properly formatted.

**Acceptance Scenarios**:

1. **Given** a directory containing multiple `.md` files with identical header/footer text, **When** the tool is run, **Then** the output files should contain only the unique content with headers/footers removed.
2. **Given** a markdown file where paragraphs are split across multiple lines (e.g., words cut off at the end of a line), **When** the tool is run, **Then** these lines should be merged into a single paragraph in the output.
3. **Given** two distinct paragraphs on subsequent lines, **When** the tool is run, **Then** an empty line should be inserted between them.

---

### User Story 2 - Preserve Directory Structure (Priority: P2)

As a user with a large collection of organized documents, I want the processed files to be saved in a mirrored directory structure so that I don't lose my organization.

**Why this priority**: High value for usability with large datasets. Ensures the tool integrates into existing workflows.

**Independent Test**: Can be tested by providing a nested input directory and verifying the output directory has the same hierarchy.

**Acceptance Scenarios**:

1. **Given** an input directory `input/` with subdirectories `A/` and `B/`, **When** the tool is run with output directory `output/`, **Then** the files should appear in `output/A/` and `output/output/B/` respectively.

---

### Edge Cases

- **Empty Files**: If an input file is empty, the output file should also be empty (or skipped).
- **No Headers/Footers**: If no repeating text is found, the content should remain unchanged except for paragraph formatting.
- **Short Files**: Files with very little text should not have their unique content accidentally flagged as a header/footer.
- **Non-matching Files**: Files that do not match the input mask MUST be ignored and NOT copied to the output directory.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST recursively scan the input directory for files matching a user-provided input mask (e.g., `*.md`). If no mask is provided, it MUST default to `*.md`.
- **FR-001a**: The system MUST ignore any files in the input directory that do not match the specified input mask.
- **FR-002**: The system MUST replicate the directory structure of the input directory into the output directory.
- **FR-003**: The system MUST detect repeating text blocks (lines) across the input files using statistical analysis. Lines appearing in more than 50% of files or repeated frequently within single files MUST be identified as headers/footers.
- **FR-003a**: The system MUST NOT remove page numbering patterns (e.g., "# Page 3", "1-1") even if they appear frequently.
- **FR-003b**: The system MUST use a two-pass processing strategy: the first pass MUST count line frequencies globally across all matching files, and the second pass MUST perform the cleaning based on those frequencies.
- **FR-004**: The system MUST remove identified headers and footers from the output files.
- **FR-005**: The system MUST merge subsequent lines that are part of the same paragraph. Lines starting with markdown structural symbols (e.g., `-`, `*`, `#`, `|`, `>`) MUST NOT be merged into preceding or succeeding lines.
- **FR-006**: The system MUST ensure that every new paragraph is preceded by exactly one empty line.
- **FR-007**: The system MUST be executable via a CLI interface taking input and output directory paths as arguments.
- **FR-008**: The system MUST overwrite any existing files in the output directory if they share the same relative path as a processed input file.

### Key Entities

- **Input Directory**: The source location containing the raw OCR markdown files.
- **Output Directory**: The destination where processed files are stored.
- **Processed File**: A markdown file that has been cleaned of headers/footers and had its paragraphs reformatted.
- **Text Block**: A sequence of characters/lines analyzed for repetition.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `.md` files in the input directory are processed and present in the output directory.
- **SC-002**: The output directory structure exactly matches the input directory structure.
- **SC-003**: At least 95% of recurring headers and footers (appearing in >50% of files) are successfully removed.
- **SC-004**: All paragraph-internal line breaks (lines not ending in sentence-ending punctuation or followed by an empty line) are merged.
- **SC-005**: Every distinct paragraph in the output is separated by exactly one blank line.
