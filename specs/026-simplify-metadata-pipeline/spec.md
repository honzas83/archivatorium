# Feature Specification: Simplify Metadata Pipeline

**Feature Branch**: `026-simplify-metadata-pipeline`

**Created**: 2026-06-09

**Status**: Draft

**Input**: User description: "Simplify the production metadata pipeline and remove obsolete topic modes. The metadata command must default vault_root to output_dir and pdf_dir to output_dir for compatibility, but generated source links must be derived from the mirrored output layout, not from the input PDF lookup directory. Generated PDFs must always be mirrored into pdf/, and generated source links must point to [[pdf/<filename>.pdf]]. The hierarchy file and tags file must remain explicit required command options. The intended production command is: python -m ocrpolish.cli metadata NATO_NPG_source NATO_NPG_metadata.v5 --hierarchy-file topics/NATO_themes.yaml --tags-file topics/USEFUL_TAGS.yaml. Non-flat topic extraction must be removed from the production codebase. The old TopicExtractor and two-step/non-flat topic extraction path must be removed from runtime metadata processing and from the production test suite. If old evaluation scripts are still useful, they must live outside the package runtime path and must not define production behaviour. Flat topic extraction must be the only production topic extraction mode. Tests for production behaviour must focus on the flat TaggingService path. MetadataProcessor.process_file must be refactored into an explicit internal pipeline while preserving observable output behaviour. The pipeline stages should be: read source, parse source and strip generated sections, extract document metadata, extract generated tags, reconcile metadata and tags, render frontmatter, render callouts, write output, and ingest generated output tags. Each stage must expose testable inputs and outputs so regressions can be covered independently. The tagging service must precompute static taxonomy prompt text and useful tag prompt text during initialization. Since flat topic extraction is the production path, flattened taxonomy should be computed once and reused for every chunk. Sliding-window tagging must not repeatedly dump taxonomy YAML or rebuild static prompt sections per window. The refactor must preserve existing compatible metadata-output behaviour: mirrored source structure, Obsidian vault initialization, Metadata/Abstract/Citation callout ordering, citation generation, page counting from page headers, and interlinking compatibility."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run the simplified production command (Priority: P1)

As a pipeline operator, I want the metadata command to work with explicit hierarchy and tag files while defaulting compatible output locations, so that production runs can use the shorter canonical command without losing existing vault behaviour.

**Why this priority**: This is the entry point for production use and protects compatibility for existing metadata runs.

**Independent Test**: Can be tested by running the metadata command with an input directory, output directory, hierarchy file, and tags file, without supplying vault or PDF output options, then inspecting the generated vault and links.

**Acceptance Scenarios**:

1. **Given** an input directory `NATO_NPG_source` and output directory `NATO_NPG_metadata.v5`, **When** the operator runs metadata processing with `--hierarchy-file topics/NATO_themes.yaml --tags-file topics/USEFUL_TAGS.yaml`, **Then** the run accepts the command without requiring separate vault or PDF output locations.
2. **Given** a generated Markdown output for `folder/document.md`, **When** the source PDF is available through the production lookup process, **Then** the PDF is mirrored into the output vault under `pdf/document.pdf` and the generated source link is `[[pdf/document.pdf]]`.
3. **Given** omitted hierarchy or tags file options, **When** the operator starts metadata processing, **Then** the command fails before processing and clearly identifies the missing required option.

---

### User Story 2 - Use only flat production topic extraction (Priority: P1)

As a maintainer, I want production metadata processing to have a single flat topic extraction path, so that runtime behaviour and tests no longer depend on obsolete non-flat topic modes.

**Why this priority**: Multiple topic modes increase maintenance cost and make production output harder to reason about.

**Independent Test**: Can be tested by searching production metadata processing and production tests for non-flat topic mode entry points, then running metadata extraction and verifying that topic extraction uses the flat tagging service path only.

**Acceptance Scenarios**:

1. **Given** production metadata processing, **When** topic extraction is requested, **Then** flat topic extraction is the only selectable production mode.
2. **Given** obsolete two-step or non-flat topic extraction code, **When** the production package is inspected, **Then** it is absent from the runtime metadata path and cannot define production behaviour.
3. **Given** old evaluation scripts that remain useful, **When** they are retained, **Then** they live outside the production package runtime path and are clearly separated from production behaviour.

---

### User Story 3 - Preserve metadata output while exposing pipeline stages (Priority: P2)

As a maintainer, I want file processing split into explicit, independently testable stages, so that regressions in reading, stripping, extraction, reconciliation, rendering, writing, and tag ingestion can be isolated without changing the generated vault output.

**Why this priority**: The refactor is valuable only if it improves testability while preserving existing metadata-output compatibility.

**Independent Test**: Can be tested by calling each processing stage with controlled inputs and asserting its output, then comparing a full processed file against existing compatible output expectations.

**Acceptance Scenarios**:

1. **Given** source Markdown with existing generated sections, **When** the parse-and-strip stage runs, **Then** it returns the source body without generated frontmatter or generated callouts and exposes the stripped content for downstream extraction.
2. **Given** extracted document metadata and generated tags, **When** reconciliation runs, **Then** it produces one coherent output model used by frontmatter rendering, callout rendering, and generated-output tag ingestion.
3. **Given** a full metadata processing run, **When** output is written, **Then** the mirrored source structure, Obsidian vault initialization, Metadata/Abstract/Citation callout ordering, citation generation, page counting from page headers, and interlinking compatibility remain unchanged from the compatible behaviour.

---

### User Story 4 - Avoid repeated static prompt construction (Priority: P3)

As a pipeline operator, I want sliding-window tagging to reuse static taxonomy and useful-tag prompt text, so that large documents do not repeatedly rebuild the same prompt sections for every window.

**Why this priority**: This improves throughput and reduces avoidable work without changing classification semantics.

**Independent Test**: Can be tested by processing a multi-window document and verifying that the flattened taxonomy and static prompt text are prepared once for the tagging service instance and reused across windows.

**Acceptance Scenarios**:

1. **Given** a tagging service initialized with a hierarchy file and useful tags file, **When** multiple chunks are tagged, **Then** the flattened taxonomy and static prompt sections are reused instead of rebuilt for each chunk.
2. **Given** a sliding-window tagging run, **When** prompts are prepared for each window, **Then** each prompt uses the same precomputed taxonomy and useful-tag text with only per-window document content changing.

### Edge Cases

- If `vault_root` is omitted, it defaults to the output directory while preserving Obsidian vault initialization.
- If `pdf_dir` is omitted, it defaults to the output directory for compatibility, but generated source links still use the mirrored output vault path under `pdf/`.
- If a source PDF is discovered in an input lookup directory, the generated Markdown never links to that lookup path; it links only to the mirrored vault PDF path.
- If an output filename would collide in the mirrored `pdf/` folder, the run must resolve or report the conflict before producing an ambiguous source link.
- If old non-flat topic tests remain in the repository, they must not be part of the production test suite or assert production behaviour.
- If a source file has no page headers, page counting retains the existing compatible fallback behaviour.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The metadata command MUST require explicit hierarchy file and tags file options for production metadata processing.
- **FR-002**: The metadata command MUST default `vault_root` to the output directory when no vault root is provided.
- **FR-003**: The metadata command MUST default `pdf_dir` to the output directory when no PDF directory is provided.
- **FR-004**: Generated PDFs MUST always be mirrored into a `pdf/` directory inside the generated output vault.
- **FR-005**: Generated source links MUST be derived from the mirrored output layout and MUST use the format `[[pdf/<filename>.pdf]]`.
- **FR-006**: Generated source links MUST NOT be derived from, or expose, the input PDF lookup directory.
- **FR-007**: The production command MUST support the form `python -m ocrpolish.cli metadata <input_dir> <output_dir> --hierarchy-file <hierarchy_file> --tags-file <tags_file>` without requiring additional vault or PDF path options.
- **FR-008**: Flat topic extraction MUST be the only production topic extraction mode.
- **FR-009**: Obsolete non-flat, two-step topic extraction MUST be removed from runtime metadata processing.
- **FR-010**: The old `TopicExtractor` production runtime path MUST be removed or made unavailable to production metadata processing.
- **FR-011**: Production behaviour tests MUST focus on the flat tagging service path and MUST NOT assert obsolete non-flat production behaviour.
- **FR-012**: Retained evaluation-only scripts for old topic extraction approaches MUST live outside the production package runtime path and MUST NOT define production metadata behaviour.
- **FR-013**: File metadata processing MUST expose explicit stages with testable inputs and outputs: read source, parse source and strip generated sections, extract document metadata, extract generated tags, reconcile metadata and tags, render frontmatter, render callouts, write output, and ingest generated output tags.
- **FR-014**: The staged file-processing pipeline MUST preserve the observable generated output behaviour of the existing compatible metadata pipeline.
- **FR-015**: Metadata/Abstract/Citation callouts MUST retain their existing generated order.
- **FR-016**: Citation generation MUST remain compatible with existing metadata output expectations.
- **FR-017**: Page counting from page headers MUST remain compatible with existing metadata output expectations.
- **FR-018**: Generated output MUST preserve mirrored source directory structure.
- **FR-019**: Generated output MUST preserve Obsidian vault initialization behaviour.
- **FR-020**: Generated output MUST preserve interlinking compatibility.
- **FR-021**: The tagging service MUST prepare static taxonomy prompt text and useful-tag prompt text during initialization.
- **FR-022**: The flattened taxonomy used by flat topic extraction MUST be computed once per tagging service initialization and reused for every chunk processed by that service.
- **FR-023**: Sliding-window tagging MUST NOT repeatedly dump taxonomy data or rebuild static taxonomy and useful-tag prompt sections per window.

### Key Entities *(include if feature involves data)*

- **Metadata Command Configuration**: The effective command inputs and defaults, including input directory, output directory, hierarchy file, tags file, vault root, and PDF directory.
- **Mirrored PDF Source Link**: The generated vault-relative source reference that points to a PDF mirrored under `pdf/`.
- **Flat Tagging Service Path**: The single production topic and tag extraction path that uses flattened taxonomy and useful tags.
- **Processing Stage Result**: The explicit input and output record for each stage of file processing, used to test and preserve behaviour independently.
- **Reconciled Metadata Output**: The unified output data used to render frontmatter, callouts, citations, links, and generated tag ingestion.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of production metadata runs using the intended command form succeed without requiring explicit vault or PDF output path options.
- **SC-002**: 100% of generated source links in processed Markdown files point to `[[pdf/<filename>.pdf]]` paths inside the output vault.
- **SC-003**: 100% of generated PDFs for processed files are present in the output vault's `pdf/` directory or the run reports a clear processing failure for the affected file.
- **SC-004**: Production metadata processing exposes no selectable non-flat topic extraction mode.
- **SC-005**: Production tests for topic extraction exercise the flat tagging service path only.
- **SC-006**: Each file-processing stage can be tested independently with controlled inputs and expected outputs.
- **SC-007**: A regression comparison over representative metadata outputs shows no unintended changes to mirrored structure, Obsidian initialization, callout order, citations, page counts, or interlink-compatible links.
- **SC-008**: For a document requiring at least three tagging windows, static taxonomy and useful-tag prompt sections are prepared once per tagging service instance and reused across all windows.

## Assumptions

- **A-001**: The output directory is the intended Obsidian vault root unless the operator explicitly provides another vault root.
- **A-002**: The generated `pdf/` folder is the canonical location for source PDFs referenced from generated Markdown.
- **A-003**: Existing compatible metadata-output behaviour is defined by the current production expectations and regression tests, not by obsolete evaluation scripts.
- **A-004**: Flat topic extraction is accepted as the sole production mode; historical non-flat evaluation remains optional and non-production.
