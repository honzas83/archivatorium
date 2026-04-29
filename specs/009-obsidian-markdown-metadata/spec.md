# Feature Specification: Obsidian Markdown Metadata

**Feature Branch**: `009-obsidian-markdown-metadata`  
**Created**: 2026-04-29  
**Status**: Draft  
**Input**: User description: "Now, we will change the format of generated metadata into Markdown to better suit Obsidian. So we will not use nested properties (https://obsidian.md/help/properties), we will convert hashtags into Obsidian tags (https://obsidian.md/help/tags) We will use attachments to refer to the orignal PDF (https://obsidian.md/help/attachments) In this feature, we will still operate on a level of single-file."

## Clarifications

### Session 2026-04-29
- Q: How should the system handle the source PDF link if it's in another directory? → A: Use relative path (Option B).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Obsidian Native Metadata (Priority: P1)

As a researcher using Obsidian, I want my OCR-processed documents to have metadata in a format that Obsidian understands natively, so that I can easily search and link my research notes without manual reformatting.

**Why this priority**: This is the core requirement of the feature. Without Obsidian-compatible metadata, the research workflow is fragmented.

**Independent Test**: Process a single PDF and verify the output is a `.md` file with a valid YAML frontmatter containing all extracted metadata fields at the top level.

**Acceptance Scenarios**:

1. **Given** a PDF file and its extracted metadata, **When** the processing is complete, **Then** a `.md` file is created with a YAML frontmatter block.
2. **Given** extracted metadata with nested structures, **When** the Markdown file is generated, **Then** all nested properties are flattened into top-level keys.
3. **Given** an extracted `abstract`, **When** the Markdown file is generated, **Then** the abstract content is also included as an Obsidian `[!abstract]` callout at the top of the document body.

---

### User Story 2 - Source Document Linking (Priority: P2)

As a researcher, I want a direct link from my Markdown note to the original source PDF, so I can quickly refer back to the original document for verification or deeper study.

**Why this priority**: Maintaining the connection between processed text and source material is critical for research integrity.

**Independent Test**: Check the generated `.md` file for an Obsidian-style internal link `[[path/to/filename.pdf]]`.

**Acceptance Scenarios**:

1. **Given** an input file `research.pdf`, **When** the metadata is generated, **Then** the resulting `.md` file includes a link formatted as `[[path/to/research.pdf]]` using the relative path from the vault root.

---

### User Story 3 - Obsidian Tag Integration (Priority: P3)

As a researcher, I want keywords identified in the document to be available as Obsidian tags, so I can use Obsidian's tag navigation and graph view to explore my document collection.

**Why this priority**: Tags are a primary navigation method in Obsidian; having them correctly formatted enables better discovery.

**Independent Test**: Verify that any "hashtags" or "keywords" in the metadata are formatted as `#tag` or placed in a `tags` property recognized by Obsidian.

**Acceptance Scenarios**:

1. **Given** metadata containing hashtags (e.g., "#NATO", "#Security"), **When** the Markdown is generated, **Then** these are represented as Obsidian-compatible tags.

---

### Edge Cases

- **Missing Source PDF**: How does the system handle generating a link if the source PDF filename is unknown or missing? (Assumption: The input filename is always known).
- **Duplicate Property Keys**: What happens when flattening results in two identical keys? (e.g., `author.name` and `editor.name` both becoming `name`).
- **Special Characters in Tags**: How are tags with spaces or special characters handled to remain valid Obsidian tags?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST output metadata as a Markdown file (`.md`).
- **FR-002**: Metadata MUST be contained within a YAML frontmatter block at the start of the file.
- **FR-003**: All metadata properties MUST be top-level; the system MUST NOT use nested YAML objects.
- **FR-004**: System MUST include an Obsidian-style attachment link `[[path/to/source_filename.pdf]]` to the original source file using the relative path from the vault root.
- **FR-005**: System MUST convert metadata keywords/hashtags into Obsidian-compatible tags.
- **FR-006**: System MUST operate on a single-file processing level.
- FR-007: System MUST handle the flattening of nested structures by joining keys with underscores (e.g., `author_name`).
- FR-008: System MUST place the PDF attachment link as a property in the YAML frontmatter (e.g., `source: "[[path/to/filename.pdf]]"`).

### Key Entities *(include if feature involves data)*

- **Metadata Note**: The output Markdown file containing the processed information.
- **Source PDF**: The original document being referred to via an attachment link.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of generated files are valid Markdown files that can be opened by Obsidian.
- **SC-002**: Obsidian Properties view successfully parses and displays all metadata fields.
- **SC-003**: The PDF attachment link correctly resolves to the source file within an Obsidian vault.
- **SC-004**: Metadata contains zero nested YAML objects.

## Assumptions

- **A-001**: The output Markdown file is intended to be stored in the same Obsidian vault as the source PDF (or a subfolder thereof) for the attachment link to work.
- **A-002**: The input to this feature is the raw metadata extracted by the LLM (from feature 008).
