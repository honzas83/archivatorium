# Feature Specification: Preserve Metadata Directory Structure

**Feature Branch**: `017-preserve-metadata-structure`  
**Created**: 2026-05-06  
**Status**: Draft  
**Input**: User description: "For metadata command, I want to keep the directory structure the same as in the source PDF / Markdown tree. Basically copy (if hardlinks are available, use them) the original structure, but the MD files will be enriched with metadata frontmatter and callouts."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mirror Directory Structure (Priority: P1)

As a user, I want the output of the metadata command to exactly mirror the directory hierarchy of my source files so that I can maintain my existing organization in my Obsidian vault.

**Why this priority**: Core requirement of the request. Essential for organized knowledge management.

**Independent Test**: Can be tested by running the metadata command on a nested directory and verifying that the output directory has the same subfolder structure.

**Acceptance Scenarios**:

1. **Given** a source directory with multiple levels of nested subfolders containing PDF and MD files, **When** the metadata command is executed, **Then** the output directory must contain the same folder hierarchy.
2. **Given** a file at `source/project-a/notes.md`, **When** processed, **Then** the enriched file must appear at `output/project-a/notes.md`.

---

### User Story 2 - Efficient File Mirroring (Priority: P2)

As a user, I want the system to use hardlinks for files where possible to save disk space and time, especially for large source files.

**Why this priority**: Improves performance and reduces disk usage, as requested by the user.

**Independent Test**: Can be tested by checking the link count or inode of files in the output directory compared to the source directory.

**Acceptance Scenarios**:

1. **Given** a source file that does not require modification (e.g., non-markdown assets if applicable), **When** mirrored, **Then** it should be a hardlink to the source file if they are on the same filesystem.
2. **Given** a source file that requires enrichment, **When** processed, **Then** a new file is created at the target path (as it must be modified).

---

### User Story 3 - Enriched Markdown Files (Priority: P1)

As a user, I want Markdown files in the mirrored structure to be enriched with metadata frontmatter and callouts while preserving their original content.

**Why this priority**: Core functional value of the metadata command.

**Independent Test**: Can be tested by inspecting an output MD file to ensure it contains both original content and new metadata sections.

**Acceptance Scenarios**:

1. **Given** an MD file in a source subfolder, **When** processed, **Then** the corresponding MD file in the output subfolder must contain the YAML frontmatter and LLM-extracted callouts.
2. **Given** a PDF file in a source subfolder, **When** processed, **Then** the resulting MD file must be placed in the equivalent output subfolder.

### User Story 4 - Organized PDF Storage (Priority: P2)

As a user, I want PDFs to be stored in a `pdf/` subdirectory within their respective mirrored folders to avoid cluttering the main directory, and I want the links in the Markdown files to point to these new locations.

**Why this priority**: Improves vault organization and reduces visual clutter.

**Independent Test**: Can be tested by verifying that PDF files appear in a `pdf/` subfolder and the corresponding MD file has a link formatted as `[[pdf/filename.pdf]]`.

**Acceptance Scenarios**:

1. **Given** a source file `folder/doc.pdf`, **When** mirrored, **Then** it must be placed at `output/folder/pdf/doc.pdf`.
2. **Given** a corresponding markdown file `folder/doc.md`, **When** enriched, **Then** its `source` property in frontmatter must be `[[pdf/doc.pdf]]`.

### User Story 5 - Safe BibTeX Identifiers (Priority: P2)

As a user, I want BibTeX identifiers to use only safe characters so that they are compatible with all LaTeX tools and citation managers.

**Why this priority**: Prevents syntax errors in bibliography management.

**Independent Test**: Can be tested by verifying that a document with a code like `NPG(SG)N(68)1` generates a BibTeX key like `NPG-SG-N-68-1`.

**Acceptance Scenarios**:

1. **Given** a document with archive code `NPG(SG)N(68)1`, **When** BibTeX is generated, **Then** the key must be `NPG-SG-N-68-1`.
2. **Given** a document with archive code `AC/137-D/498`, **When** BibTeX is generated, **Then** the key must be `AC-137-D-498`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST recursively scan the input directory for PDF and Markdown files.
- **FR-002**: System MUST replicate the exact directory structure of the input directory into the output directory.
- **FR-003**: System MUST create the target directories before writing any files.
- **FR-004**: System MUST attempt to use hardlinks (`os.link`) for mirroring files that do not require modification (if supported by the filesystem).
- **FR-005**: System MUST fallback to copying files if hardlinking is not possible or if the file needs modification.
- **FR-006**: System MUST enrich Markdown files with metadata (frontmatter and callouts) as per existing metadata extraction logic.
- **FR-007**: System MUST handle filenames with special characters and spaces correctly.
- **FR-008**: System MUST place PDF files in a `pdf/` subdirectory within their target mirrored directory.
- **FR-009**: System MUST update the `source` link in Markdown files to point to the `pdf/` subdirectory.
- **FR-010**: System MUST normalize BibTeX and URL identifiers to include only alphanumeric characters, hyphens, underscores, and colons.

### Key Entities

- **Source Tree**: The input directory hierarchy containing documents to be processed.
- **Output Tree**: The mirrored directory hierarchy containing enriched documents.
- **Processed Document**: A Markdown file that has been enriched with metadata.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of the directory structure from the source is replicated in the output.
- **SC-002**: All Markdown files in the output tree contain the expected metadata sections.
- **SC-003**: Processing time for mirroring (excluding LLM calls) is minimized by using hardlinks where possible.
- **SC-004**: The system correctly handles nested directories at least 10 levels deep.
