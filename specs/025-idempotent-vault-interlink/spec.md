# Feature Specification: Idempotent Vault Interlinking and Finalization

**Feature Branch**: `025-idempotent-vault-interlink`

**Created**: 2026-06-09

**Status**: Draft

**Input**: User description: "Create one idempotent `interlink VAULT_DIR` vault-finalization workflow that operates only on the generated output vault. It must interlink generated documents and produce Markdown index pages plus XLSX export from the canonical generated tag model..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Idempotent Vault Interlinking (Priority: P1)

As a vault administrator, I want to run `interlink` on the generated vault directory to cross-reference documents by archive_code, add language version links, and enrich metadata tables without corrupting the files or creating duplicate/nested links when re-running the command multiple times.

**Why this priority**: Essential for establishing reliable, stable cross-references across documents in the generated Obsidian vault. Without idempotency, multiple runs corrupt files.

**Independent Test**: Can be tested by running the interlink command once on a clean generated vault, verifying all links are correct, then running it a second time and verifying the file hashes or contents are unchanged (idempotency), with no nested links like `[[ [[link]] ]]` or duplicate table rows.

**Acceptance Scenarios**:

1. **Given** a generated vault with files containing references to other files by `archive_code` (e.g. `NPG/D(74)2`), **When** `ocrpolish interlink VAULT_DIR` is executed, **Then** all mentions of archive codes are replaced with standard Markdown links (e.g. `[[path/to/NPG-D-74-2.md|NPG/D(74)2]]`) using full vault-relative Markdown paths, Metadata table references are enriched, and `language_versions` are added when appropriate.
2. **Given** an already interlinked vault, **When** `ocrpolish interlink VAULT_DIR` is run again, **Then** the files remain unchanged and links are not nested (no `[[ [[...]] ]]`), and references or language versions are not duplicated.
3. **Given** a vault document referencing itself, **When** interlinking runs, **Then** the document MUST NOT link to itself (self-linking prevention).

---

### User Story 2 - Markdown Index Generation (Priority: P2)

As an Obsidian vault user, I want to browse generated index files (for States, Cities, Organizations, People, Topics, and Tags) built from the prefix tags (`#Entities/...`, `#Topics/...`, `#Tags/...`) to easily navigate the vault contents.

**Why this priority**: Enhances vault navigability based on the authoritative tag model.

**Independent Test**: Run `interlink` on the vault, check that `Index - States.md`, `Index - Cities.md`, etc., are created/overwritten in the vault directory, containing alphabetical lists of tags and links to source documents.

**Acceptance Scenarios**:

1. **Given** a vault directory containing processed documents with tags like `#Entities/State/US`, `#Entities/Org/NATO`, `#Topics/Nuclear-Deterrence`, **When** `ocrpolish interlink VAULT_DIR` is executed, **Then** index files (`Index - States.md`, `Index - Cities.md`, `Index - Organizations.md`, `Index - People.md`, `Index - Topics.md`, and `Index - Tags.md`) are generated in `VAULT_DIR`.
2. **Given** the index files are generated, **When** they are inspected, **Then** States, Organizations, People, Topics, and Tags are sorted alphabetically, and Cities are grouped under their parent State, and all index files list matching documents.
3. **Given** generated index files are present from a previous run, **When** `ocrpolish interlink VAULT_DIR` is run, **Then** they are overwritten deterministically and excluded from the shared scan of source documents.

---

### User Story 3 - XLSX Metadata Export with Canonical Tags & Citekey (Priority: P3)

As a researcher, I want to export the vault's metadata to a `metadata_index.xlsx` spreadsheet containing core document metadata (including stable `citekey`) and pivoted columns for States, Cities, Organizations, People, Topics, and Tags, so that I can analyze the corpus using spreadsheet tools.

**Why this priority**: Enables external analysis and reconciliation of vault documents with reference managers or external databases.

**Independent Test**: Check that `metadata_index.xlsx` is generated in `VAULT_DIR`, containing a row for each source document with columns for core metadata (including `citekey`) and the canonical tags, with values matching the generated Markdown indices.

**Acceptance Scenarios**:

1. **Given** a vault with processed markdown files, **When** `ocrpolish interlink VAULT_DIR` is run, **Then** a `metadata_index.xlsx` file is generated in `VAULT_DIR`.
2. **Given** the generated `metadata_index.xlsx`, **When** its structure is checked, **Then** it contains core document metadata columns (including `citekey`) and separate columns for State, City, Org, Person, Topic, and conceptual tags, but pivots away from Pydantic model fields and does not include obsolete `mentioned_*` columns.
3. **Given** a document with canonical tags, **When** XLSX and Markdown indices are generated, **Then** they reflect identical tag values parsed using the same canonical tag parser.

---

### Edge Cases

- **What happens if a document contains obsolete unprefixed tags (e.g. `#State/...`) instead of the canonical `#Entities/State/...`?**
  The workflow must ignore obsolete unprefixed tags in the normal production path and only parse prefixed `#Entities/...`, `#Topics/...`, and `#Tags/...`.
- **What happens if the `interlink` command is run multiple times on a vault with modified/updated user edits?**
  Since the workflow is idempotent, it parses updated files, applies interlinking safely, and regenerates index pages and the spreadsheet deterministically.
- **What happens if a generated index file or `metadata_index.xlsx` already exists in `VAULT_DIR`?**
  The shared scan MUST exclude these files and not treat them as source documents.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The CLI command MUST be registered as `ocrpolish interlink VAULT_DIR`. It MUST NOT require a source input directory or separate output directory.
- **FR-002**: The workflow MUST scan `VAULT_DIR` exactly once at the beginning into shared document records in memory.
- **FR-003**: The shared scan MUST exclude all generated non-document outputs, including:
  - Index pages (`Index - *.md`)
  - Spreadsheet (`metadata_index.xlsx`)
  - Templates/template files (e.g., `templates/`, `obsidian_template/` contents, or folders containing them)
  - Other known generated vault support files (e.g., `.obsidian/` configs).
- **FR-004**: Each scanned document record in memory MUST contain: `vault-relative path`, `frontmatter metadata`, `source body`, `archive_code`, `language`, `raw references`, `generated tags`, `entities`, and `topics`.
- **FR-005**: Interlinking MUST run before index and XLSX generation.
- **FR-006**: Interlinking MUST resolve `archive_code` references using full vault-relative Markdown paths, enrich the Metadata table references in each document, and add `language_versions` where appropriate, while preserving the YAML frontmatter. It MUST NOT mutate generated tags.
- **FR-007**: Every operation in the interlink workflow MUST be idempotent:
  - Links MUST NOT be nested (e.g., no `[[ [[link]] ]]` or double bracket wrapping).
  - References and language_versions rows in the Metadata table MUST NOT be duplicated.
  - Index pages MUST be overwritten deterministically.
  - `metadata_index.xlsx` MUST be regenerated deterministically.
- **FR-008**: If interlinking makes any changes to document files, the workflow MUST update the in-memory document records or reparse the changed documents before producing Markdown indices and XLSX outputs.
- **FR-009**: Indexing and XLSX generation MUST parse tags (`#Entities/...`, `#Topics/...`, `#Tags/...`) using the canonical tag parser.
- **FR-010**: States, City, Org, Person, Topic, and conceptual tag indices MUST be generated from these authoritative tags, and MUST NOT depend on obsolete unprefixed tags (such as `#State/...` or `#Org/...`).
- **FR-011**: Generated Markdown index pages MUST cover: `Index - States.md`, `Index - Cities.md`, `Index - Organizations.md`, `Index - People.md`, `Index - Topics.md`, and `Index - Tags.md`.
- **FR-012**: In index pages: States, organizations, people, topics, and conceptual tags MUST be grouped alphabetically; cities MUST be grouped by parent state.
- **FR-013**: XLSX export MUST pivot away from `MetadataSchema.model_fields` and obsolete `mentioned_*` columns. It MUST export core document metadata plus generated-tag-model columns for State, City, Org, Person, Topic, and conceptual tag values.
- **FR-014**: Core document metadata exported to XLSX MUST include `citekey` so spreadsheet exports, frontmatter, Metadata tables, and BibTeX citations can be reconciled by the same stable citation key.
- **FR-015**: The XLSX export MUST use the same canonical tag parser and resume counters as the Markdown index generation, ensuring that all output values are identical.

### Key Entities *(include if feature involves data)*

- **ScannedDocument**: In-memory record holding document details (path, body, frontmatter, archive_code, language, references, tags, etc.).
- **MarkdownIndexPage**: A generated index file (e.g. `Index - States.md`) listing source documents grouped and formatted as Markdown.
- **MetadataIndexExcel**: The generated `metadata_index.xlsx` spreadsheet representing core metadata and pivoted tag model columns.
- **ArchiveCodeResolver**: Component responsible for resolving archive_code values to vault-relative paths.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running `ocrpolish interlink VAULT_DIR` on a vault containing 100 documents completes in under 10 seconds.
- **SC-002**: Subsequent runs of `ocrpolish interlink VAULT_DIR` produce identical file outputs (zero byte difference) if no source documents have changed.
- **SC-003**: 100% of generated index pages and spreadsheet columns contain tags parsed exclusively using the canonical tag parser.
- **SC-004**: No generated links are nested (i.e. no nested double-brackets) and no reference rows in the Metadata table are duplicated.

## Assumptions

- **A-001**: The generated vault directory `VAULT_DIR` is passed as a valid local directory path.
- **A-002**: The YAML frontmatter in source documents follows a standard format that can be parsed and dumped using `PyYAML` without loss of custom user fields.
- **A-003**: The canonical tag parser supports extracting entities, topics, and tags from `#Entities/State/...`, `#Entities/City/...`, `#Entities/Org/...`, `#Entities/Person/...`, `#Topics/...`, and `#Tags/...`.
