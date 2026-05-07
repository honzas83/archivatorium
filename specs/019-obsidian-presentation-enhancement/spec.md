# Feature Specification: Obsidian Presentation Enhancement

**Feature Branch**: `019-obsidian-presentation-enhancement`  
**Created**: 2026-05-07  
**Status**: Draft  
**Input**: User description: "This specification will improve presentation in Obsidian. Fix of Bibtex citation: @misc{NPG-D-73-10, author = {Luff, E. F.}, title = {Nuclear Planning Group: Consultation Procedures and Facilities Detailed Examination of Selected Aspects}, date = {1973-10-05}, note = {Nuclear Planning Group, NPG/D(73)10, NATO Archive Obsidian}, url = {https://nato-obsidian.kky.zcu.cz/NPG-D-73-10}, urldate = {2026-05-07} } Look in @nato_npg_metadata.v4/.obsidian/app.json and appearance.json a generate exactly those files at the beginning of metadata run. Put also @nato_npg_metadata.v4/CONTENT.base into the root. Since the properties are hidden, we need to create a new callout with the visual representation of frontmatter fields. Look into @nato_npg_metadata.v4/MUSTR_metadata_table2.md . In Category/Topic reason, if there is direct citation in quotes like "" or '', normalize it to "" and format as Markdown italic"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Obsidian Workspace Initialization (Priority: P1)

As a researcher using Obsidian, I want the output directory to be automatically configured as a ready-to-use vault with specific settings and a base content file.

**Why this priority**: Essential for the "presentation in Obsidian" goal, ensuring the vault behaves as expected (e.g., hidden properties) immediately after generation.

**Independent Test**: Run the metadata extraction process on a source directory and verify that `.obsidian/app.json`, `.obsidian/appearance.json`, and `CONTENT.base` exist in the output root with correct content.

**Acceptance Scenarios**:

1. **Given** a source directory and an empty output directory, **When** the metadata run starts, **Then** `.obsidian/app.json` and `.obsidian/appearance.json` are created in the output directory.
2. **Given** the initialization phase, **When** `CONTENT.base` is found in the reference path, **Then** it is copied to the root of the output directory.

---

### User Story 2 - Visual Metadata Presentation (Priority: P1)

As an Obsidian user, I want to see a formatted table of document metadata within the note itself, because frontmatter properties are hidden by vault settings.

**Why this priority**: Core requirement for visual improvement. Properties are hidden by `app.json` settings, so a visual substitute is required.

**Independent Test**: Open a generated markdown file in Obsidian and verify that an `[!info] Metadata` callout is present at the top with a formatted table.

**Acceptance Scenarios**:

1. **Given** a document with frontmatter metadata, **When** the markdown file is generated, **Then** an `[!info] Metadata` callout is inserted before the content.
2. **Given** the metadata callout, **When** rendered, **Then** it contains a table with icons (≡, №, 🗓, 🔗, ☰) corresponding to the fields defined in `MUSTR_metadata_table2.md`.
3. **Given** a document, **When** generated, **Then** an `[!abstract]` callout and a `[!citing this document]` callout are also included.

---

### User Story 3 - Normalized Topic Citations (Priority: P2)

As an editor, I want citations within the "Category/Topic reason" section to be consistently formatted so that they are easily distinguishable and look professional.

**Why this priority**: Improves readability and consistency of the AI-generated descriptions.

**Independent Test**: Check the "Categories/Topics" section of a generated file. Any quoted text in the reason should be wrapped in double quotes and italicized.

**Acceptance Scenarios**:

1. **Given** a topic reason containing `'single quoted text'`, **When** processed, **Then** it becomes `_"single quoted text"_`.
2. **Given** a topic reason containing `"double quoted text"`, **When** processed, **Then** it becomes `_"double quoted text"_`.

---

### User Story 5 - Improved Tagging Precision (Priority: P2)

As a curator, I want the AI-generated tags and reasons to follow specific linguistic and formatting rules to ensure high-quality metadata.

**Why this priority**: Improves the quality and professional appearance of the generated tagging data.

**Independent Test**: Review tagging results for a document mentioning non-abbreviation entities (e.g., "PERSHING") and verify they are Title Cased. Check topic reasons for the presence of direct citations.

**Acceptance Scenarios**:

1. **Given** a document mentioning a missile name in uppercase ("PERSHING"), **When** tagged, **Then** the resulting tag is "Pershing" (unless identified as a strict acronym).
2. **Given** a topic extraction prompt, **When** the LLM generates a reason, **Then** it is encouraged to include direct citations from the text.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST copy `.obsidian/app.json` and `.obsidian/appearance.json` from the `obsidian_template` directory to the output directory at the start of execution.
- **FR-002**: System MUST copy `CONTENT.base` from `obsidian_template` to the output root.
- **FR-003**: System MUST generate an `[!info] Metadata` callout containing a formatted table:
    - **Headerless**: The explicit "Field | Value" header row is removed. The first metadata field (**title**) serves as the technical table header to ensure Markdown validity while maintaining a minimalist visual style.
    - **Bold Emphasis**: Critical labels (**title**, **pages**, **date**) and their corresponding values MUST be bolded.
    - **PDF Reference**: The `source` field (Icon: 🔗) MUST be placed immediately after the `pages` field.
    - **List Presentation**: Multi-value fields (e.g., references) MUST use `<br>` tags to render each item on a separate line within the table cell.
    - **Icons**: Include specified icons (≡, №, 🗓, 🔗, ☰) as defined in the layout.
- **FR-004**: System MUST generate an `[!abstract]` callout containing the document summary and mentioned entities.
- **FR-005**: System MUST generate a `[!citing this document]` callout at the end of the metadata section, featuring Chicago, Harvard, and updated BibTeX formats.
- **FR-006**: System MUST update the BibTeX template to use `date = {YYYY-MM-DD}` and match the structure provided in the user request.
- **FR-007**: System MUST post-process "Category/Topic reason" text to replace any single or double quotes around direct citations with double quotes and Markdown italic markers (e.g., `_"citation"_`).
- **FR-008**: System MUST instruct the LLM to include direct citations in topic reasons.
- **FR-009**: System MUST instruct the LLM to use Title Case for uppercase tags that are not abbreviations (e.g., "Pershing" instead of "PERSHING").

### Key Entities

- **Obsidian Vault**: The output directory containing configured settings and processed markdown files.
- **Metadata Callout**: A visual block within a markdown file that renders hidden property data for the user.
- **Citations**: Formatted bibliographic references (Chicago, Harvard, BibTeX) included in the document.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of generated output directories contain valid `.obsidian` configurations.
- **SC-002**: Metadata callouts are present in 100% of generated markdown files, featuring bold critical fields and multi-line reference lists.
- **SC-003**: All citations in Topic reasons are normalized to `_"text"_` format and displayed in bulleted lists.
- **SC-004**: BibTeX citations successfully validate against the requested `@misc` structure.
- **SC-005**: Vault settings correctly hide standard properties in Obsidian (verified by `app.json` content).
- **SC-006**: At least 80% of topic reasons in a sample run contain direct citations.
- **SC-007**: 100% of identified non-abbreviation uppercase entities are converted to Title Case in tags.
