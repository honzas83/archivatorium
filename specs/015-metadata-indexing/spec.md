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

As a knowledge manager, I want to have index pages in my Obsidian vault that group documents by State, City, and Topic so that I can easily navigate the collection.

**Why this priority**: Essential for the Obsidian vault experience, providing entry points into the graph based on common entities.

**Independent Test**: Run `python -m ocrpolish.cli index vault_dir`. Verify that `Index - States.md`, `Index - Cities.md`, and `Index - Topics.md` are created in the vault.

**Acceptance Scenarios**:

1. **Given** documents containing `#State/Canada` and `#State/Belgium`, **When** the index is generated, **Then** `Index - States.md` shows alphabetical sections (B, C) with lists of documents associated with those states.
2. **Given** documents with `#City/Belgium/Brussels`, **When** the index is generated, **Then** `Index - Cities.md` groups cities under their respective states (Belgium -> Brussels).
3. **Given** a topics YAML file, **When** the index is generated, **Then** `Index - Topics.md` shows a hierarchical list of categories and topics with their descriptions.

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
- **Conflicting Tags**: If an entity appears both in frontmatter and the abstract, it should only be counted once per document for the index.
- **Missing Topics YAML**: If generating a topic index but no YAML is provided, the tool should either fallback to using tags found in documents or error out if the YAML is mandatory.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a `index` subcommand accepting an `INPUT_DIR`.
- **FR-002**: System MUST recursively scan `INPUT_DIR` for `.md` files.
- **FR-003**: System MUST parse YAML frontmatter from each document.
- **FR-004**: System MUST parse the `[!abstract]` callout block in the document body to extract hierarchical tags (e.g., `#State/...`, `#City/...`, `#Org/...`, `#Category/Topic`).
- **FR-005**: System MUST generate an XLSX file if `--output-xlsx` is provided, with columns matching the project's metadata schema.
- **FR-006**: System MUST generate `Index - States.md` with alphabetical grouping (A, B, C...) of `#State/` tags.
- **FR-007**: System MUST generate `Index - Cities.md` with grouping by state (State -> City) for `#City/` tags.
- **FR-008**: System MUST generate `Index - Topics.md` using a provided YAML for structure and descriptions.
- **FR-009**: System MUST allow specifying the path to the topics YAML file via a CLI argument (e.g., `--topics-yaml`).
- **FR-010**: System MUST save Markdown index pages in the root of `INPUT_DIR`. The path should be defined as a configurable variable relative to the vault root in the implementation.

### Key Entities *(include if feature involves data)*

- **Metadata Index**: A collection of records representing all processed documents and their associated attributes.
- **Entity Reference**: A link between a document and a specific entity (State, City, Organization, or Topic) extracted from the document's metadata or content.
- **Topic Hierarchy**: A structured definition of categories and sub-topics, including labels and descriptions, used to organize documents.

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
