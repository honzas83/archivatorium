# Feature Specification: Metadata Indexing

**Feature Branch**: `015-metadata-indexing`  
**Created**: 2026-05-04  
**Status**: Draft  
**Input**: User description: "In this feature, we will load the generated Obsidian vault with metadata (metadata subcommand) and generate index pages and XLSX index of the metadata. Command will be: python -m ocrpolish.cli index INPUT_DIR [--output-xlsx index.xlsx] Go through the input directory and load MD fields from the frontmatter. Load also entities from the abstract... For category/topic index use a provided YAML..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate XLSX Metadata Index (Priority: P1)

As a researcher, I want to export all document metadata to a spreadsheet so that I can perform bulk analysis and sorting outside of Obsidian.

**Why this priority**: Core value for researchers who need to see the "big picture" of their document collection in a structured format.

**Independent Test**: Run `python -m ocrpolish.cli index vault_dir --output-xlsx index.xlsx`. Verify `index.xlsx` exists and contains all documents from `vault_dir` with columns matching the metadata schema.

**Acceptance Scenarios**:

1. **Given** a directory containing multiple `.md` files with valid YAML frontmatter, **When** the index command is run with `--output-xlsx`, **Then** an XLSX file is created with one row per document.
2. **Given** a document with missing metadata fields, **When** exported to XLSX, **Then** the corresponding cells are left empty but the row is still created.

---

### User Story 2 - Generate Obsidian Index Pages (Priority: P1)

As a knowledge manager, I want to have index pages in my Obsidian vault that group documents by State, City, Organization, and Topic so that I can easily navigate the collection.

**Why this priority**: Essential for the Obsidian vault experience, providing entry points into the graph based on common entities.

**Independent Test**: Run `python -m ocrpolish.cli index vault_dir`. Verify that `Index - States.md`, `Index - Cities.md`, `Index - Organizations.md`, and `Index - Topics.md` are created in the vault. These pages should list the relevant hashtags (e.g., `#State/Belgium`) rather than individual document links.

**Acceptance Scenarios**:

1. **Given** documents containing `#State/Canada` and `#State/Belgium`, **When** the index is generated, **Then** `Index - States.md` shows alphabetical sections (B, C) containing the hashtags `#State/Belgium` and `#State/Canada` respectively.
2. **Given** documents with `#City/Belgium/Brussels`, **When** the index is generated, **Then** `Index - Cities.md` shows a section for `Belgium` containing the hashtag `#City/Belgium/Brussels`.
3. **Given** documents with `#Org/NATO`, **When** the index is generated, **Then** `Index - Organizations.md` lists the hashtag `#Org/NATO`.
4. **Given** a topics YAML file, **When** the index is generated, **Then** `Index - Topics.md` shows a hierarchical list of category/topic hashtags with their descriptions from the YAML.

---

### User Story 3 - Parse Abstract Callouts for Entities (Priority: P2)

As a user, I want the indexing tool to find entities mentioned in the document abstract, not just in the frontmatter, so that the index is comprehensive.

**Why this priority**: The current workflow stores many entities inside an `[!abstract]` callout rather than frontmatter properties to keep the UI clean.

**Independent Test**: Create a document with no tags in frontmatter but `#Org/NATO` inside an `[!abstract]` callout. Verify that the document appears under NATO in the generated index.

**Acceptance Scenarios**:

1. **Given** a document with `#State/Denmark` inside the `## Mentioned Entities` section of an `[!abstract]` callout, **When** indexing occurs, **Then** this document is included in the Denmark section of the State index.

---

### Edge Cases

- **Empty Vault**: If the input directory contains no `.md` files, the tool should report "No documents found" and exit gracefully.
- **Malformed Frontmatter**: Documents with invalid YAML should be skipped with a warning, but the rest of the indexing process should continue.
- **Conflicting Tags**: If an entity appears both in frontmatter and the abstract, they MUST be merged and deduplicated so each unique entity is only counted once per document for the index.
- **Missing Topics YAML**: If generating a topic index but no YAML is provided, the tool should either fallback to using tags found in documents or error out if the YAML is mandatory.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a `index` subcommand accepting an `INPUT_DIR`.
- **FR-002**: System MUST recursively scan `INPUT_DIR` for `.md` files.
- **FR-003**: System MUST parse YAML frontmatter from each document.
- **FR-004**: System MUST parse the `[!abstract]` callout block in the document body to extract hierarchical tags (e.g., `#State/...`, `#City/...`, `#Org/...`, `#Category/Topic`).
- **FR-005**: System MUST generate an XLSX file if `--output-xlsx` is provided, strictly containing columns for fields defined in the project's `MetadataSchema` Pydantic model.
- **FR-006**: System MUST generate `Index - States.md` listing `#State/` hashtags found in the vault, grouped by their first letter.
- **FR-007**: System MUST generate `Index - Cities.md` listing `#City/` hashtags found in the vault, grouped by state.
- **FR-008**: System MUST generate `Index - Organizations.md` listing `#Org/` hashtags found in the vault.
- **FR-009**: System MUST generate `Index - Topics.md` listing category/topic hashtags with descriptions from the provided topics YAML.
- **FR-010**: System MUST allow specifying the path to the topics YAML file via a CLI argument (e.g., `--topics-yaml`).
- **FR-011**: System MUST save Markdown index pages in the root of `INPUT_DIR`. The path should be defined as a configurable variable relative to the vault root in the implementation.
- **FR-012**: System MUST only index hierarchical tags with specific predefined prefixes (State, City, Org, Category), but the list of prefixes MUST be easily extensible in the source code.

### Key Entities *(include if feature involves data)*

- **Metadata Index**: A collection of records representing all processed documents and their associated attributes.
- **Entity Reference**: A link between a document and a specific entity (State, City, Organization, or Topic) extracted from the document's metadata or content.
- **Topic Hierarchy**: A structured definition of categories and sub-topics, including labels and descriptions, used to organize documents.

## Clarifications

### Session 2026-05-04
- Q: Should a dedicated index for Organizations be created? → A: Yes, create `Index - Organizations.md` and be prepared to extend the list to other entities.
- Q: Should the indexer automatically discover and index all hierarchical tag prefixes or stick to a predefined list? → A: Stick to a predefined list (States, Cities, Organizations, Topics).
- Q: How should conflicting metadata between frontmatter and the abstract be handled? → A: Merge and deduplicate entities from both sources.
- Q: Which fields should be included in the XLSX index? → A: Only fields explicitly defined in the `MetadataSchema` Pydantic model.
- Q: How should documents be linked in the Markdown index pages? → A: Use hashtags (e.g., `#State/Belgium`) instead of full document references (e.g., `[[Doc]]`), allowing Obsidian to handle the document list via the tag.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of valid `.md` files in the vault are represented in the generated XLSX index.
- **SC-002**: Index generation for a 1,000-document vault completes in under 10 seconds.
- **SC-003**: All hierarchical tags found in `[!abstract]` callouts are correctly mapped to their respective Markdown index pages.
- **SC-004**: Generated Markdown index pages are fully compatible with Obsidian (links work, tags are recognized).
- **SC-005**: XLSX output contains no malformed rows or missing columns for standard metadata fields.

## Assumptions

- The input vault follows the structure generated by previous `ocrpolish` commands (frontmatter + abstract callout).
- The `python-docx` and `xlsxwriter` (or similar) libraries are available or can be added.
- The user has write permissions for the `INPUT_DIR` and the destination of the XLSX file.
- `Index - Topics.md` will only include topics that are actually used in the vault, unless specified otherwise.
