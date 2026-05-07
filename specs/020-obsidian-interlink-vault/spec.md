# Feature Specification: Obsidian Vault Interlinking

**Feature Branch**: `020-obsidian-interlink-vault`  
**Created**: 2026-05-07  
**Status**: Draft  
**Input**: User description: "Implement feature - new subcommand - for postprocessing the generated Obsidian vault inplace. The goal of the postprocessing should be to interlink the documents. In the first version, we will use the archive_code and language fields. At first, create a mapping from archive_code + language to filename. Then, convert the references: field to hyperlinks as well as all occurrences of references in the body. Reference to a document in the same language if you have many variants. If the archive_code exists, but not in the current language, refer to English by default or other languages. Use matching on prefix-boundary, i.e. DPC/D(69)58 matches DPC/D(69)58(Revised) but DPC/D(69)5 doesn't match it. Add another field under the language: named language_versions: and crosslink the different language versions of the same archive_code. Normalize archive_code to not contain spaces for matching purposes Use links like: Markdown: [Three laws of motion](Three laws of motion.md)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Interlink References in Metadata (Priority: P1)

As a researcher using the Obsidian vault, I want the `references:` field in my documents to be automatically converted into clickable links so that I can easily navigate between related historical documents.

**Why this priority**: This is the core functionality requested. Navigating between documents is the primary value of an interlinked vault.

**Independent Test**: Can be tested by running the subcommand on a vault with documents having `archive_code` and `references` fields, and verifying that the `references` list now contains Markdown links to existing files.

**Acceptance Scenarios**:

1. **Given** a vault with `DocA` (archive_code: `CODE1`, language: `English`) and `DocB` (references: [`CODE1`], language: `English`), **When** the interlinking command is run, **Then** `DocB`'s references should contain `[CODE1](DocA.md)`.
2. **Given** a document with a reference `DPC/D(69)58`, **When** the vault contains `DPC/D(69)58(Revised)`, **Then** it should link to the revised version (prefix matching).

---

### User Story 2 - Cross-link Language Versions (Priority: P2)

As a multilingual user, I want to see links to the same document in other languages so that I can compare translations or find the version most comfortable for me.

**Why this priority**: Enhances the value of the multilingual archive by surfacing existing translations.

**Independent Test**: Can be tested by having multiple files with the same `archive_code` but different `language` values, and verifying the `language_versions:` field is populated with links.

**Acceptance Scenarios**:

1. **Given** `Doc_EN` (CODE1, English) and `Doc_FR` (CODE1, French), **When** processed, **Then** `Doc_EN` should have `language_versions: [French: [French](Doc_FR.md)]` and `Doc_FR` should have `language_versions: [English: [English](Doc_EN.md)]`.

---

### User Story 3 - Interlink References in Document Body (Priority: P2)

As a reader, I want occurrences of archive codes within the text of a document to be converted into links so that I can follow references without scrolling back to the metadata section.

**Why this priority**: Improves the "deep" interlinking of the vault beyond just the structured metadata.

**Independent Test**: Can be tested by searching for archive code patterns in the body text and verifying they are wrapped in Markdown link syntax.

**Acceptance Scenarios**:

1. **Given** a document body containing "See also DPC/D(69)58 for details", **When** `DPC/D(69)58` exists in the vault, **Then** the text should become "See also [DPC/D(69)58](Doc_Path.md) for details".

---

### Edge Cases

- **Multiple Language Fallback**: If a reference target exists in multiple languages but not the current document's language, the system MUST prioritize English, then any other available language.
- **Prefix Collision**: `DPC/D(69)5` should NOT match `DPC/D(69)58` (prefix must end at a boundary).
- **Inplace Safety**: Ensure that if the command is run multiple times, it doesn't double-link or corrupt the files.
- **Spaces in Archive Codes**: Archive codes in files might have spaces, but matching must use a normalized version (no spaces).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST create a global mapping of `(normalized_archive_code, language)` to `filename` for all documents in the target directory.
- **FR-002**: System MUST normalize `archive_code` by removing all whitespace characters for matching purposes.
- **FR-003**: System MUST identify references in the `references:` frontmatter field and convert them to Markdown links `[Title](Filename.md)`.
- **FR-004**: System MUST identify occurrences of known `archive_code` patterns in the Markdown body and convert them to links.
- **FR-005**: System MUST use a prefix-boundary matching strategy for `archive_code` (e.g., `A/B` matches `A/B(rev)` but not `A/BC`).
- **FR-006**: System MUST link to the version of the document in the same language as the source document if available.
- **FR-007**: System MUST use English as the default fallback language if the target is not available in the source language.
- **FR-008**: System MUST add a `language_versions:` field under the `language:` key in the frontmatter, containing links to other language versions of the same document.
- **FR-009**: System MUST perform all modifications "inplace" on the existing Markdown files.

### Key Entities *(include if feature involves data)*

- **Document**: Represents an Obsidian Markdown file.
    - `archive_code`: The unique identifier for the historical document (normalized for matching).
    - `language`: The language of the document.
    - `references`: A list of other archive codes cited by this document.
    - `filename`: The relative path/name in the vault.
- **Link Mapping**: A lookup table/dictionary used to resolve `(code, lang)` to `path`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of valid `references:` entries that have a corresponding target in the vault are converted to clickable links.
- **SC-002**: 100% of documents with multiple language versions have the `language_versions:` field correctly populated with cross-links.
- **SC-003**: No broken links are generated (all generated links MUST point to an existing file in the vault).
- **SC-004**: Archive code matching avoids false positives by adhering to prefix-boundary rules (0% incorrect partial matches).
