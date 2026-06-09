# Feature Specification: Resume-Safe Metadata and Prompt Isolation

**Feature Branch**: `024-resume-safe-metadata`

**Created**: 2026-06-09

**Status**: Draft

**Input**: User description: "Make metadata processing resume-safe and prevent generated metadata from being fed back into LLM prompts."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Resume-Safe Processing with Preflight Scan (Priority: P1)

As a pipeline operator, I want metadata processing to scan the output directory before starting, so that already processed files contribute to global tag/entity counters and are skipped safely without double-counting.

**Why this priority**: Essential for resume-safety and efficiency, preventing duplicate processing and corrupting tag frequencies.

**Independent Test**: Can be tested by running the processing command on a folder, stopping it halfway, and restarting it. The system should correctly skip completed files while producing identical tag/entity counters.

**Acceptance Scenarios**:

1. **Given** a directory with 5 already processed Markdown files in the output folder, **When** processing starts with overwrite=false, **Then** the system scans the output folder exactly once, populates global counters with their tags, and skips those 5 files.
2. **Given** a skipped file, **When** the system determines its tags, **Then** they are counted towards the global frequencies only if they were not already loaded during the preflight scan.

---

### User Story 2 - Clean Markdown Content Extraction and Prompt Isolation (Priority: P1)

As a pipeline developer, I want the LLM prompt context to include only cleaned source Markdown, so that previously generated metadata callouts, abstract callouts, and frontmatter are not fed back into the LLM as context.

**Why this priority**: Prevents "hallucination loops" where the LLM repeats or is biased by previously generated metadata.

**Independent Test**: Pass an already enriched Markdown file to the processor; verify that the generated prompt sent to Ollama client contains none of the YAML frontmatter, Metadata tables, Abstract callouts, or citation blocks.

**Acceptance Scenarios**:

1. **Given** an input Markdown file that contains YAML frontmatter and generated callouts (Metadata, Abstract, Citation), **When** the system reads the content for LLM prompting, **Then** it strips all of these generated sections and feeds only the cleaned body text to the prompt.

---

### User Story 3 - Clean and Reconciled Metadata Schema (Priority: P2)

As an archive researcher, I want the output YAML frontmatter and Metadata table to contain only the canonical fields, and use a deterministic code-derived citekey instead of LLM-generated identifiers.

**Why this priority**: Eliminates obsolete fields and ensures semantic consistency between the frontmatter and the rendered table.

**Independent Test**: Verify that the generated frontmatter and metadata table contain exactly the canonical fields (including the new deterministic citekey) and that obsolete mentioned fields/tags are removed.

**Acceptance Scenarios**:

1. **Given** a processed file, **When** frontmatter and metadata table are generated, **Then** they both contain the same reconciled canonical fields, and the citekey is generated deterministically from the filename stem (or vault path in optional mode).
2. **Given** an input file with manually corrected frontmatter fields, **When** the file is re-processed, **Then** those manually corrected fields are reconciled and preserved according to explicit per-field rules.

---

### Edge Cases

- **What happens when the output folder doesn't exist yet?**
  The preflight scan is skipped gracefully without errors, and the global counters start empty.
- **How does the system handle corrupt YAML in user-supplied frontmatter?**
  The system logs a warning, skips merging the corrupt frontmatter, and proceeds with the newly extracted metadata.
- **What happens if a filename stem contains characters that are invalid in BibTeX?**
  The deterministic citekey generator replaces any unsafe characters with hyphens and collapses multiple hyphens.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Preflight scan MUST run exactly once before processing files, scanning the output directory and populating `conceptual_tag_counts`, `topic_counts`, and `entity_counts` using the `CanonicalTagParser`.
- **FR-002**: When a file is skipped (overwrite=false and output exists), the processor MUST ensure its tags contribute to the global counters, doing so only if they were not already loaded during the preflight scan.
- **FR-003**: The processor MUST strip all generated sections from the input file content before using it as context for LLM prompting. Stripped sections include: YAML frontmatter, Metadata callout block, Abstract callout block, and Citation callout block.
- **FR-004**: Cross-document consistency hints in LLM prompts (e.g., frequent tags, states, orgs, cities) MUST be derived exclusively from the global counters, and NEVER from old generated sections or frontmatter.
- **FR-005**: The `MetadataSchema` Pydantic model used for LLM extraction MUST exclude `mentioned_states`, `mentioned_organisations`, `mentioned_cities`, and `tags`.
- **FR-006**: Extraction of entities, topics, and conceptual tags MUST be delegated entirely to the tagging service/path.
- **FR-007**: The canonical metadata fields stored in frontmatter and the Metadata table MUST be restricted to: `title`, `summary` (exactly one sentence), `pages`, `source`, `sender`, `recipient`, `intent`, `author_name`, `author_institution`, `date`, `archive_code`, `citekey`, `language`, `location_city`, `location_state`, and `references`.
- **FR-008**: The `abstract` field MUST NOT be stored in the YAML frontmatter or Metadata table, but rendered in the Abstract callout.
- **FR-009**: The `citekey` field MUST be generated deterministically from the output filename stem by default, or optionally from the full vault-relative output path (excluding `.md` suffix) to prevent folder-based collisions.
- **FR-010**: The generated `citekey` MUST be normalized to safe BibTeX characters (`a-z`, `A-Z`, `0-9`, `-`, `_`, `:`) and used as the BibTeX `@misc` citation key. The `archive_code` MUST NOT be used as the BibTeX citekey.
- **FR-011**: YAML frontmatter and the rendered Metadata table/callout MUST be generated from the same reconciled metadata model and agree semantically.
- **FR-012**: If the rendered Metadata table includes deterministic derived navigation fields (such as interlinking-derived references or language versions), they MUST be explicitly labeled as derived output (e.g., `references (derived)`), without mutating YAML frontmatter.
- **FR-013**: Deterministic reconciliation of user-supplied frontmatter MUST happen after source extraction using explicit per-field rules:
  - `title`: Existing value is preserved (overrides extracted) if non-empty.
  - `summary`: Overwritten by newly extracted value.
  - `pages`: Overwritten by newly calculated value.
  - `source`: Overwritten by newly calculated value.
  - `sender`, `recipient`, `intent`: Existing value is preserved if non-empty.
  - `author_name`, `author_institution`: Existing value is preserved if non-empty.
  - `date`: Existing value is preserved if non-empty and valid.
  - `archive_code`: Existing value is preserved if non-empty.
  - `citekey`: Overwritten by newly calculated value.
  - `language`: Existing value is preserved if non-empty.
  - `location_city`, `location_state`: Existing value is preserved if non-empty.
  - `references`: Set union of existing and newly extracted references, sorted alphabetically.
  - Custom fields (not in canonical list): Always preserved.

### Key Entities *(include if feature involves data)*

- **ReconciledMetadataModel**: A unified representation of canonical document metadata (including custom user fields), used to populate YAML frontmatter and rendered tables.
- **VocabularyHints**: Compact string representation of frequent tags and entities derived from counters to provide to the LLM.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running the metadata extraction pipeline on a directory containing already processed files with `overwrite=false` completes in under 5 seconds (excluding LLM calls, which are skipped), while successfully rebuilding tag counters.
- **SC-002**: 100% of LLM prompt payloads are verified to have no YAML frontmatter, Metadata tables, or abstract callouts from previous runs.
- **SC-003**: YAML frontmatter and the rendered Metadata table semantically agree for all canonical fields in all generated output files.
- **SC-004**: BibTeX citekeys in generated `.md` files match the code-derived normalized filename stem (or vault-relative path) 100% of the time, and never fallback to archive code.

## Assumptions

- **A-001**: The output directory is only mutated by the ocrpolish tool or by direct manual user edit.
- **A-002**: The structure of the generated callouts remains consistent so they can be accurately matched and stripped by regular expressions.
