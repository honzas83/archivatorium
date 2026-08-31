# Feature Specification: Escape Non-Standard Hashtags in Vault

**Feature Branch**: `034-escape-other-hashtags`

**Created**: 2026-07-29

**Status**: Complete

**Input**: User description: "fix the interlink command to "escape" the hash characters in the document bodies so that only #Entities, #Tags and #Topics appear in the obsidian vault"

## Clarifications

### Session 2026-07-29

- Q: How should the index generation logic simplify and limit the size of these index pages? → A: Option C with a cap of 50 documents (Hybrid capped listing, listing first 50 documents, showing remaining count, and linking to Obsidian search URL).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Escape non-standard hashtags during interlinking (Priority: P1)

As a vault administrator, when I run the `interlink` command, I want any `#` characters in the markdown files that do not represent canonical Obsidian tags or markdown headers to be backslash-escaped so that Obsidian renders them as literal text instead of importing them into the tag index.

**Why this priority**: This is the core functional requirement of the feature. Without it, arbitrary document identifiers (like `#67-8` or `#67-87155`) bloat the tag pane.

**Independent Test**: Can be tested by running the interlink command on a mock document containing both valid tags (e.g. `#Entities/Org/NATO`) and invalid tag shapes (e.g. `#67-8`, `#67-87155`), verifying that only invalid tag shapes are escaped as `\#67-8` and `\#67-87155` in the document body.

**Acceptance Scenarios**:

1. **Given** a markdown file with body text `DOCUMENT DESTRUCTION MEMO. #67-87155`, **When** the interlink command processes the file, **Then** the output contains `DOCUMENT DESTRUCTION MEMO. \#67-87155`.
2. **Given** a markdown file with valid tags `#Entities/Org/NATO` and `#Topics/Defence`, **When** the interlink command processes the file, **Then** they remain unchanged.

---

### User Story 2 - Idempotency and safe escaping (Priority: P2)

When running `interlink` multiple times, already-escaped hash characters (`\#`) must not be escaped again (e.g., to `\\#`). Additionally, headers (e.g., `# Header`), tag prefixes inside code blocks/inline code, and YAML frontmatter must remain untouched.

**Why this priority**: Running the command repeatedly is a common operation. The parser must not introduce malformed escaping.

**Independent Test**: Can be tested by running the command twice on the same file and verifying the output remains unchanged.

**Acceptance Scenarios**:

1. **Given** a file with body text `DOCUMENT DESTRUCTION MEMO. \#67-87155`, **When** the interlink command processes it, **Then** it remains `DOCUMENT DESTRUCTION MEMO. \#67-87155`.
2. **Given** a header `# Page 1` and code block containing `#comment`, **When** the interlink command processes the file, **Then** they remain unchanged.

---

### Edge Cases

- **Code Blocks and Inline Code**: If the document contains code blocks or inline code with `#` (e.g. comment lines like `# comment` or config properties), they must not be escaped because that would break code formatting and syntax.
- **YAML Frontmatter**: The Frontmatter section is metadata and must not have its `#` characters escaped (though tags in frontmatter are usually defined as plain lists, if there are any comments or hashes, they must remain intact).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The `interlink` command MUST escape any raw `#` characters in document bodies that are not part of valid/canonical tags or markdown headers.
- **FR-002**: Valid/canonical tags that MUST NOT be escaped are those starting with `#Entities/`, `#Topics/`, or `#Tags/`.
- **FR-003**: Markdown headers (e.g. `# Header`, `## Header`, etc., where `#` is at the beginning of a line followed by a space) MUST NOT be escaped.
- **FR-004**: The escaping mechanism MUST be idempotent, meaning a pre-existing escaped hash `\#` MUST NOT be escaped again (e.g. to `\\#`).
- **FR-005**: Hash characters inside inline code (surrounded by backticks `` ` ``) or code blocks (fenced by ```) MUST NOT be escaped.
- **FR-006**: Hash characters inside YAML frontmatter MUST NOT be escaped.
- **FR-007**: The index page generation MUST limit the number of inline document links listed under each tag or entity key to a maximum of 50.
- **FR-008**: If a tag or entity key is associated with more than 50 documents, the index page MUST list only the first 50 documents, state the remaining count (e.g., "and 142 more..."), and provide a native Obsidian search URL link to query all matching documents (e.g., `[Search in Vault](obsidian://search?query=...)`).
- **FR-009**: The search URL MUST format the query appropriately (e.g., `tag:%23Tags/DefencePlanning` for tags, or `tag:%23Entities/Org/NATO` for entities).

### Non-Functional Requirements

- **NFR-001**: The selective escaping logic MUST use a fast-path check (`"#" not in text`) to instantly bypass parsing execution for documents containing no hash characters, optimizing total execution speed.
- **NFR-002**: The selective escaping logic MUST be implemented using C-optimized Python string methods (e.g. `.find()`, `.count()`, `.startswith()`) and slice operations on a per-line basis instead of character-by-character loops or a single complex regular expression, to maximize performance, readability, and correct edge-case handling.

### Key Entities

- **VaultDocument**: Represents a markdown file in the Obsidian vault, containing frontmatter, metadata callout, abstract, main body, and citations.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of non-standard hashtags (like `#67-8` or `#67-87155`) in the markdown bodies of the processed vault are successfully escaped as `\#` prefix.
- **SC-002**: 100% of canonical tags (beginning with `#Entities/`, `#Topics/`, `#Tags/`) are preserved as-is.
- **SC-003**: The `interlink` command remains fully idempotent; executing the command repeatedly on the same vault produces identical content.
- **SC-004**: No markdown headers, code block contents, or frontmatter YAML values are modified or broken by the escaping mechanism.
- **SC-005**: All generated index files (e.g., `Index - Tags.md`) list a maximum of 50 document links per tag/entity, significantly reducing file size for 30k vaults.
- **SC-006**: For any tag/entity with >50 documents, a valid and functional Obsidian search link is appended to allow the user to view the full list of matching documents.
- **SC-007**: Vault processing speed matches or exceeds baseline interlink performance, with the selective escaping logic adding negligible overhead (less than 1ms per file average).

## Assumptions

- Standard markdown parser behavior applies for escaping (Obsidian correctly renders `\#` as a literal `#` character and ignores it for tag indexation).
- The escaping logic only needs to process files during the `interlink` command execution.
- Only `.md` files in the vault are subject to this escaping.
