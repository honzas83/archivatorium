# Feature Specification: Ollama Metadata Extraction

**Feature Branch**: `008-ollama-metadata-extraction`  
**Created**: 2026-04-28  
**Status**: Final  
**Input**: User description: "Now, we will add a new functionality for metadata extraction. I want to use ollama with gemma4:26b model with schema enforcement to extract the following metadata: 1st level metadata (typically first page), catalogue Author Institution (Organisation) Officer name Date of the document Last date in the whole body Archive code in the form NPG/D(77)12 Title Letter from X to Y Untitled - summary Abstract Language Location ? State Mentioned states The metadata will be added as headers into MD files in the output directory. Make it executable as a new command."

## User Scenarios & Testing

### User Story 1 - Batch Metadata Extraction (Priority: P1)
As a researcher, I want to automatically extract structured metadata from a large collection of OCR-processed Markdown files so that I can easily catalog and search through my documents.

**Acceptance Scenarios**:
1. **Batch Processing**: System processes directories in strict alphabetical order.
2. **Directory Mirroring**: Input directory structure is replicated in output.

---

### User Story 2 - Consistent Tagging & Thematic Linking (Priority: P2)
As an archivist, I want the system to maintain thematic consistency across documents by reusing relevant tags and avoiding generic noise.

**Acceptance Scenarios**:
1. **Tag Accumulation**: System tracks tag frequency across the run and passes the top 50 as context to the LLM.
2. **Specific Tagging**: LLM is instructed to avoid generic tags (e.g., #ColdWar) in favor of distinguishing ones (3-8 tags per doc).

---

### User Story 3 - High Fidelity Archival Metadata (Priority: P1)
As a historian, I need the extracted data to be clean, normalized, and accurate despite OCR errors.

**Acceptance Scenarios**:
1. **Normalization**: Names/Titles in ALL CAPS are Title Cased, while whitelisted acronyms (NATO, NPG, etc.) are preserved.
2. **OCR Error Handling**: LLM interprets "CTAN" as "OTAN" by using document context.
3. **Double Delimiter Prevention**: Final MD files have exactly one `---` block at the top.

## Requirements

### Functional Requirements
- **FR-001**: System MUST provide `ocrpolish metadata` CLI command.
- **FR-002**: System MUST use local Ollama instance with schema enforcement.
- **FR-003**: System MUST support recursive directory processing and mirroring.
- **FR-004**: System MUST enforce strict schema rules:
    - `title`: Careful extraction from first 2 pages; contextually consistent.
    - `summary`: Exactly 2 sentences; independent entity (define abbreviations).
    - `abstract`: Superset of summary; max 20 sentences; independent entity.
    - `date`: ISO 8601 format (YYYY-MM-DD); 2-pass extraction for large docs.
    - `correspondence`: Validated sender/recipient/transaction; omitted if empty/"N/A".
- **FR-005**: System MUST accumulate run-wide tag frequency to ensure cross-document consistency.
- **FR-006**: System MUST normalize casing while preserving specific NATO/archival acronyms.
- **FR-007**: System MUST process files in strict alphabetical order.
- **FR-008**: System MUST extract the `title` in its **ORIGINAL LANGUAGE**.
- **FR-009**: System MUST enforce **natural casing** for titles: **Title Case** for English, **Sentence case** for French. Strictly no ALL UPPERCASE.
- FR-010: System MUST show a visual progress bar during batch processing.
- FR-011: System MUST recursively copy ALL files from the `obsidian_template` directory (if it exists) to the output vault root during initialization.


### Non-Functional Requirements
- **NFR-001**: LLM prompts MUST be optimized for `gemma4:26b` to avoid Status 500 errors (flattened schema, required fields with defaults).
- **NFR-002**: YAML frontmatter MUST be merged with existing metadata if present, without creating double delimiters.

## Success Criteria

### Measurable Outcomes
- **SC-001**: 100% of readable files processed in alphabetical order.
- **SC-002**: All output files contain a single valid YAML frontmatter block.
- **SC-003**: Archive codes match NATO patterns like `[A-Z]+/[A-Z](\d+)\d+`.
- **SC-004**: Tag consistency: Top 50 frequent tags used as LLM context in subsequent files.
- **SC-005**: Normalization: Whitelisted acronyms are never lowercase/Title Case.
