# Research & Design Decisions: Idempotent Vault Interlinking

This document details the research, choices, and design rationales for the unified, idempotent vault finalization workflow.

## Decision 1: Shared Vault Scanner and Generated File Exclusion
- **Decision**: Implement a single-pass scanner using `pathlib.Path.rglob("*.md")` that filters out:
  - Files matching `Index - *.md` (the generated index pages).
  - Config files or subdirectories like `.obsidian/` and template directories.
  - Non-markdown files such as `metadata_index.xlsx`.
  It loads all documents into an in-memory repository of `VaultDocument` records.
- **Rationale**: Scanning exactly once ensures the indexing and XLSX export do not process the generated index files as source text, which would pollute the entity/tag counters.
- **Alternatives Considered**: 
  - Dynamic scanning based on git status. Rejected because it is complex, slow, and not portable.
  - Multi-pass scanning. Rejected as it degrades performance needlessly.

## Decision 2: In-Memory Record Updating / Reparsing
- **Decision**: When the interlinking phase writes changes to a document file, the workflow will re-parse that file from disk or update its in-memory record (`VaultDocument` and its parsed tags) before passing the records to the indexing and XLSX generators.
- **Rationale**: Interlinking might modify the Markdown body (adding links) or the Metadata table (enriching references and language versions). Reparsing/updating ensuring the generated index pages and spreadsheet rows reflect the final file state.
- **Alternatives Considered**:
  - Incremental string replacements in memory. Rejected because parsing is fast enough and reparsing from the modified content guarantees correctness.

## Decision 3: Idempotent Link Resolution (Prevents Link Nesting)
- **Decision**: Modify the regex and replacement logic in `InterlinkingService` so that:
  - Any already-wrapped link (like `[[some-path|some-code]]` or `[[some-path]]`) matching an archive code is skipped and not wrapped again.
  - Standardizing search boundaries so matching archive codes are replaced only if they are not already inside markdown link syntax.
- **Rationale**: Crucial for idempotency; ensures running `ocrpolish interlink` repeatedly results in zero byte changes.
- **Alternatives Considered**:
  - Simple global string replaces. Rejected because it repeatedly wraps links on subsequent runs.

## Decision 4: Pivot to Canonical Tag-Model in XLSX and Markdown Indices
- **Decision**: Use `CanonicalTagParser` to extract State, City, Org, Person, Topic, and conceptual tags starting with `#Entities/`, `#Topics/`, or `#Tags/`. In XLSX and Markdown indices, pivot completely to columns representing these canonical prefixes and ignore obsolete, unprefixed tags like `#State/` or `#Org/`.
- **Rationale**: Standardizes the tagging schema across both Markdown navigation indexes and XLSX spreadsheet exports, ensuring consistent tag representation.
- **Alternatives Considered**:
  - Preserving legacy columns for backward compatibility. Rejected because the requirement explicitly states to pivot away from obsolete mentioned columns and unprefixed tags.
