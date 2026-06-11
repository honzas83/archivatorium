# Feature Specification: OCR Pipeline Integration

**Feature Branch**: `030-ocr-pipeline`

**Created**: 2026-06-11

**Status**: Draft

**Input**: User description: "Analyze codes in @ocr and we would like to integrate the OCR code into the ocrpolish pipeline as a separate ocr command. The prompts must be kept as is. The semantics of commands must be consistent with the rest of the ocrpolish. If the processing is interupted, the re-processing must validate the already existing outputs and if there is a non-recognized page (even a single page in the document), take the context (previous page) and perform OCR again. The goal is to recognize new pages and quality check already existing and re-recognize missing pages."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Process Directory of PDFs (Priority: P1)

As a user, I want to run `ocrpolish ocr` on a directory of PDFs so that they are converted to structured Markdown files while maintaining the directory hierarchy.

**Why this priority**: Core functionality of the pipeline to transform raw PDFs into text for further processing.

**Independent Test**: Can be tested by running the command on a directory with a single PDF and verifying a `.md` file is produced in the output directory.

**Acceptance Scenarios**:

1. **Given** an input directory containing PDFs, **When** I run the `ocr` command, **Then** Markdown files with identical base names are created in the output directory reflecting the original directory structure.
2. **Given** a multipage PDF, **When** the OCR command processes it, **Then** the output Markdown contains text separated by page headers (e.g. `---` and `# Page {i}`).

---

### User Story 2 - Resilient Interruption and Missing Page Recovery (Priority: P1)

As a user, if the OCR process is interrupted or fails on specific pages, I want to re-run the command and have it only process the missing or non-recognized pages, saving time and API costs.

**Why this priority**: Essential for long-running batch jobs that may encounter network timeouts or API errors with Ollama.

**Independent Test**: Can be tested by manually deleting a page's content from a generated Markdown file and re-running the command. Only the deleted page should be processed by the VLM.

**Acceptance Scenarios**:

1. **Given** an existing output Markdown file missing page 3, **When** I run the `ocr` command, **Then** it validates the existing output, identifies page 3 is missing, extracts the text of page 2 as context, and runs OCR only for page 3.
2. **Given** a fully recognized document, **When** I run the `ocr` command, **Then** it validates the output and skips OCR entirely.
3. **Given** a non-recognized page (e.g. empty or containing error text), **When** I run the `ocr` command, **Then** it performs OCR again for that page.

---

### Edge Cases

- What happens when the first page (Page 1) is missing? (No previous context is available; it must be processed with empty context).
- How does system handle PDFs with zero pages or corrupted PDFs?
- How does the system handle Ollama API connection failures or timeouts during page recovery?
- What constitutes a "non-recognized" page? (e.g., is it just missing from the Markdown, or does it have an empty string?)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a new `ocr` subcommand in the `ocrpolish` CLI (e.g., `ocrpolish ocr <input_dir> <output_dir>`).
- **FR-002**: System MUST recursively process all `.pdf` files in the `<input_dir>` and mirror the directory structure in `<output_dir>`.
- **FR-003**: System MUST accept OCR options including Ollama host, user, password, model, and DPI, with reasonable defaults.
- **FR-004**: System MUST use the exact `SYSTEM_PROMPT` and `USER_PROMPT` from the original `ocr/ocr_multipage_tiff_ollama.py` script (now integrated and removed) without modification.
- **FR-005**: System MUST parse existing Markdown files in the output directory to determine which pages have already been successfully processed.
- **FR-006**: System MUST skip pages that are already recognized and present in the Markdown.
- **FR-007**: System MUST re-run OCR for any page that is missing or identified as "non-recognized" (e.g., empty content).
- **FR-008**: System MUST provide the transcribed text of the *previous* page as context when re-recognizing a missing page, if a previous page exists.
- **FR-009**: System MUST update the existing Markdown file by correctly inserting the newly recognized pages in the proper sequential order.

### Key Entities

- **OCR Document Status**: Tracks the state of a PDF and its corresponding Markdown file, including `total_pages` and a mapping of `page_number -> content`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Resuming an interrupted OCR job skips at least 99% of already processed pages without calling the VLM API.
- **SC-002**: Missing pages injected into an existing Markdown file are placed in the correct sequential position 100% of the time.
- **SC-003**: The command line interface matches the semantics of other `ocrpolish` commands (e.g., `clean`, `metadata`).
- **SC-004**: System gracefully recovers from temporary Ollama API failures and timeouts during batch processing.

## Assumptions

- Target PDFs are readable by `PyPDF2` (for page counting) and `pdf2image` (for rendering).
- The output Markdown format is strictly structured with page separators (e.g. `--- \n\n # Page X \n\n`) allowing reliable parsing of page content.
- A "non-recognized page" is defined as a page missing from the Markdown entirely or having whitespace-only content.
- The `qwen3.5:9b` or `qwen3-vl:4b` Ollama models are available on the specified host.
