# Feature Specification: Zotero Citation Import

**Feature Branch**: `028-zotero-citation-import`

**Created**: 2026-06-09

**Status**: Final

**Input**: User description: "In this feature, add support for Zotero import into the Citation callout. But I don't want --zotero flag, I want to generate Zotera citations instantly as well as the other citations. Fix code and backpropagate to specification."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate Zotero CSL-JSON in Citation Callouts (Priority: P1)

As a user, I want the system to automatically generate an invisible HTML COinS (ContextObjects in Spans) string inside the Citation callout, alongside Chicago, Harvard, and BibTeX citations, so that I can easily import the document's metadata directly into Zotero via a browser extension.

**Why this priority**: This enables rapid and automated import of documents into Zotero by leveraging the metadata already extracted by Ollama, making integration seamless.

**Independent Test**: Can be tested by running the processing pipeline (`metadata` command) on a sample document and verifying that the resulting markdown file contains a correctly formatted CSL-JSON block in the Citation callout.

**Acceptance Scenarios**:

1. **Given** a directory of processed markdown documents, **When** the user runs the metadata command, **Then** the generated Citation callouts correctly include the HTML COinS span containing the metadata.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST NOT require an external Zotero file to be passed via the CLI.
- **FR-002**: System MUST generate an invisible HTML COinS (ContextObjects in Spans) `<span class="Z3988">` tag inside the citation callout containing the document metadata formatted as a URL-encoded OpenURL.
- **FR-003**: The COinS span MUST specify `info:ofi/fmt:kev:mtx:dc` as the format and set `"rft.type"` to `"document"`. It must also include the document's language and citation key alongside standard bibliographic fields.

### Key Entities

- **COinS**: ContextObjects in Spans, a method for embedding bibliographic metadata into the HTML of web pages.
- **Citation Callout**: The specific Obsidian UI component (callout block) in the markdown document that displays bibliographic metadata.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of successfully processed documents have their Citation callouts populated with a valid COinS span.

## Assumptions

- Zotero and other extensions will correctly parse the generated `mtx:dc` OpenURL spans when the markdown is rendered to HTML.
- The output format for the Citation callouts remains consistent with the existing project format and styling constraints.
