# Feature Specification: Metadata Correctness Fixes

**Feature Branch**: `027-fix-metadata-correctness`

**Created**: 2026-06-09

**Status**: Draft

**Input**: User description: "Implement the remaining internal correctness fixes for OCRPolish metadata/tagging/finalization."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Resume Counts Only Generated Documents (Priority: P1)

An archivist resumes a metadata run against an existing vault and expects resumed tag counters to reflect only real generated document outputs, not index pages, templates, support files, sidecars, or other generated vault infrastructure.

**Why this priority**: Incorrect resume counters contaminate future tagging and can cause support or template vocabulary to influence archival document metadata.

**Independent Test**: Can be tested by preparing a vault with generated document pages plus index, template, support, and sidecar files, then resuming metadata processing and verifying only generated document pages contribute to counters.

**Acceptance Scenarios**:

1. **Given** a vault containing generated document pages and `Index - *.md` files with tags not found in documents, **When** metadata processing resumes, **Then** tags that appear only in the index pages do not affect resumed counters.
2. **Given** a skipped existing generated output that was already scanned during preflight, **When** overwrite is disabled, **Then** the skipped output is counted exactly once.
3. **Given** a skipped existing generated output that was not scanned during preflight, **When** overwrite is disabled, **Then** its canonical tags are parsed once and added to resumed counters.

---

### User Story 2 - Substantive Documents Always Receive Conceptual Tags (Priority: P1)

An archivist processes substantive source documents and expects each generated output to include meaningful `#Tags/...` conceptual tag paths alongside topics and entities.

**Why this priority**: Outputs with topics and entities but no conceptual tags are incomplete and reduce search, browsing, and reuse value in the archive.

**Independent Test**: Can be tested by processing substantive documents with policy, organizational, procedural, exercise, command, weapon, or reference content and verifying each successful output includes at least three justified conceptual tag paths.

**Acceptance Scenarios**:

1. **Given** a substantive source document, **When** tagging succeeds, **Then** the generated output includes at least three justified conceptual tag paths and the `## Tags` section is present.
2. **Given** a substantive source document whose tagging result omits, empties, or undersizes conceptual tags, **When** processing validates the result, **Then** the document fails with an explicit tagging-quality error and no incomplete output is silently accepted.
3. **Given** a genuinely non-substantive administrative stub containing only replacement, cancellation, incorporation, or equivalent bilingual boilerplate, **When** tagging validates the result, **Then** an empty conceptual tag list may be accepted.
4. **Given** a short source that mentions substantive archival content, **When** non-substantive detection runs, **Then** short length alone does not allow empty conceptual tags.

---

### User Story 3 - Canonical Tags Stay Authoritative End-to-End (Priority: P2)

An archivist exports indexes and spreadsheets from a vault and expects only canonical `#Topics/...`, `#Entities/...`, and `#Tags/...` data to populate production metadata views.

**Why this priority**: Legacy unprefixed or obsolete tag formats must not re-enter canonical outputs after the canonical model has been established.

**Independent Test**: Can be tested by adding obsolete tags to generated pages and verifying index and spreadsheet exports ignore or report them without treating them as canonical data.

**Acceptance Scenarios**:

1. **Given** generated pages containing obsolete unprefixed tags such as `#State/...`, `#Org/...`, `#City/...`, `#Person/...`, `#Category/...`, or `#Topic/...`, **When** production indexing or spreadsheet export runs, **Then** those obsolete tags do not populate canonical index or spreadsheet columns.
2. **Given** generated pages containing canonical tags, **When** production indexing or spreadsheet export runs, **Then** canonical columns are populated only from the canonical tag model.

---

### User Story 4 - Masked and Dry Runs Respect User Intent (Priority: P3)

An operator uses metadata command safety options and expects masks to limit enrichment targets and dry runs to avoid all output mutation.

**Why this priority**: Safety options must be trustworthy in automated and exploratory runs.

**Independent Test**: Can be tested by running metadata processing with a narrow mask and with dry-run enabled, then verifying enrichment scope and filesystem changes.

**Acceptance Scenarios**:

1. **Given** a metadata run with a mask, **When** Markdown files do not match the mask, **Then** they are not sent for metadata enrichment or tagging enrichment.
2. **Given** `.filtered.md` sidecar files, **When** metadata processing discovers inputs, **Then** sidecars are not enriched.
3. **Given** a metadata dry run, **When** processing completes, **Then** no vault templates, generated Markdown, mirrored PDFs, copied or linked non-Markdown files, sidecars, or existing output files are created or updated.

### Edge Cases

- A generated document page is skipped because overwrite is disabled after preflight has already scanned it.
- A generated document page is skipped because overwrite is disabled but was outside the preflight scan set.
- Tags appear only in index pages, vault landing pages, templates, metadata spreadsheet files, hidden folders, support folders, or sidecar files.
- A short source contains substantive policy, organizational, procedural, exercise, command, weapon, or reference content.
- A source contains only administrative replacement, cancellation, incorporation, or equivalent bilingual boilerplate.
- Conceptual tags overlap with entity names, topic components, acronyms, exercise names, hierarchical path components, or preferred vocabulary terms.
- A conceptual tag is a hierarchical path such as `#Tags/WINTEX/73` and must be treated as valid canonical conceptual data.
- A mask excludes Markdown files while source-tree mirroring remains enabled.
- A dry run encounters existing outputs, missing output folders, source PDFs, or non-Markdown files that would normally be mirrored.
- A source PDF belongs to a nested source folder and must be mirrored into the generated Markdown file's containing folder under a local `pdf/` subdirectory.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST preserve the existing canonical tag model as the sole production model for topics, entities, and conceptual tags.
- **FR-002**: The system MUST NOT introduce a new tag model, metadata model, or finalization command for this feature.
- **FR-003**: Resume preflight scanning MUST inspect only generated document Markdown outputs.
- **FR-004**: Resume preflight scanning MUST use the same generated-document exclusion rules used by interlinking and finalization scans.
- **FR-005**: Resume preflight scanning MUST exclude `Index - *.md`, vault landing/support `index.md` files, `metadata_index.xlsx`, template files and folders, hidden or system folders, `.filtered.md` files, and known generated vault support files.
- **FR-006**: Tags found only in generated index pages, templates, support files, or other excluded files MUST NOT affect resumed counters.
- **FR-007**: Skipped existing outputs MUST be counted exactly once.
- **FR-008**: If preflight already scanned a skipped output, skip handling MUST NOT add that output to counters again.
- **FR-009**: If preflight did not scan a skipped output and overwrite is disabled, skip handling MUST parse that generated output and add its canonical tags once.
- **FR-010**: Rebuilt conceptual tag counters MUST be passed into the tagging pass as compact reuse hints for conceptual tag extraction.
- **FR-011**: Rebuilt entity counters MUST be passed into the tagging pass as compact reuse hints for entity extraction.
- **FR-012**: Rebuilt topic counters MAY be passed into the tagging pass only as hints subordinate to the configured taxonomy.
- **FR-013**: Generated summaries, abstracts, metadata tables, citation blocks, old frontmatter tags, and legacy mentioned fields MUST remain excluded from all enrichment prompts.
- **FR-014**: Conceptual tag extraction MUST be an active required category of the initial tagging pass for substantive source documents, distinct from topic and entity extraction.
- **FR-015**: The tagging request for substantive documents MUST make `conceptual_tags` explicit and require at least three conceptual tags.
- **FR-016**: The tagging request MUST NOT impose a hard maximum count for conceptual tags.
- **FR-017**: The tagging prompt MUST state that substantive documents require at least three conceptual tags, should include every clearly justified useful conceptual tag, and may return an empty list only for non-substantive administrative stubs.
- **FR-018**: The base tagging prompt MUST replace permissive conceptual-tag wording with mandatory substantive-document wording rather than appending a contradictory instruction.
- **FR-019**: Parsed tagging results for substantive documents MUST fail validation when conceptual tags are omitted, empty, or fewer than three.
- **FR-020**: Processing MUST fail with an explicit tagging-quality error when a substantive document lacks enough conceptual tags from the initial tagging pass.
- **FR-021**: Processing MUST NOT perform a separate conceptual-tag repair phase.
- **FR-022**: Processing MUST NOT write or accept generated output that silently lacks the `## Tags` section for a substantive source.
- **FR-023**: The system MUST deterministically classify a source as non-substantive before accepting empty conceptual tags.
- **FR-024**: A source MAY be classified as non-substantive only when its cleaned text contains no meaningful archival discussion beyond administrative replacement, cancellation, incorporation, or equivalent bilingual boilerplate.
- **FR-025**: Short length alone MUST NOT classify a source as non-substantive when it contains substantive policy, organizational, procedural, exercise, command, weapon, or reference content.
- **FR-026**: If non-substantive classification is uncertain, the source MUST be treated as substantive.
- **FR-027**: Conceptual tag normalization and duplicate suppression MUST NOT remove all useful conceptual tags merely because related entities or topics exist.
- **FR-028**: Duplicate suppression SHOULD remove exact conceptual duplicates of entity names or topic components while preserving justified archival concepts, acronyms, exercise names, and hierarchical conceptual tag paths from preferred vocabulary.
- **FR-029**: Acronyms and exercise names from the useful-tags vocabulary or resumed conceptual counters MUST be preserved when substantively mentioned.
- **FR-030**: The static useful-tags vocabulary MUST remain preferred conceptual vocabulary.
- **FR-031**: Resume-derived conceptual tag counters MUST be presented as dynamic preferred conceptual vocabulary.
- **FR-032**: The tagging pass MAY create new canonical conceptual tags when justified by source text, while preferring static useful-tags vocabulary and resumed counters.
- **FR-033**: Production indexing and spreadsheet export MUST NOT import, migrate, reinterpret, or populate canonical data from obsolete unprefixed tags.
- **FR-034**: Obsolete unprefixed tags MAY be ignored or reported, but MUST NOT populate canonical index or spreadsheet columns.
- **FR-035**: If metadata masking remains exposed, matching MUST restrict which Markdown files may be sent to metadata enrichment or tagging enrichment.
- **FR-036**: Non-matching Markdown files MAY be mirrored only when source-tree mirroring is intentionally enabled, but MUST NOT be enriched.
- **FR-037**: `.filtered.md` sidecar files MUST NOT be enriched.
- **FR-038**: If metadata dry-run remains exposed, it MUST be non-mutating.
- **FR-039**: Dry-run processing MUST NOT initialize vault templates, write generated Markdown, mirror PDFs into `pdf/`, copy or hardlink non-Markdown files, write sidecars, or update any output file.
- **FR-040**: Dry-run processing MAY scan inputs, compute planned output paths, and report planned actions.
- **FR-041**: Canonical conceptual tags MAY be hierarchical paths under `#Tags/...`; valid examples include exercise/year paths such as `#Tags/WINTEX/73`.
- **FR-042**: Parsing, resume counters, indexing, spreadsheet export, duplicate suppression, and generated output rendering MUST preserve the full canonical conceptual tag path for hierarchical `#Tags/...` values.
- **FR-043**: When metadata processing mirrors a source PDF, it MUST place the PDF in a `pdf/` subdirectory beside the generated Markdown output for that source-relative folder, not in a single output-root `pdf/` directory.
- **FR-044**: Generated Markdown source links to mirrored PDFs MUST remain relative to the generated Markdown file, such as `[[pdf/NPG-D(73)11_FRE.pdf]]`.

### Key Entities *(include if feature involves data)*

- **Generated Document Output**: A Markdown page produced for a source document and eligible for resume counter reconstruction, interlinking, finalization, indexing, and export.
- **Generated Support File**: A vault file such as an index, landing page, template, spreadsheet, hidden/system file, sidecar, or support artifact that must not influence resumed document counters.
- **Canonical Tag**: An authoritative tag belonging to the existing topic, entity, or conceptual tag namespaces; conceptual tags may be hierarchical paths under `#Tags/...`.
- **Resume Counter**: Reconstructed counts of canonical tags found in generated document outputs and used as compact reuse hints during subsequent tagging.
- **Substantive Source Document**: A source whose cleaned text contains meaningful archival discussion and therefore requires conceptual tags.
- **Non-Substantive Administrative Stub**: A source whose cleaned text contains only administrative replacement, cancellation, incorporation, or equivalent bilingual boilerplate and no meaningful archival discussion.
- **Obsolete Tag**: A legacy or unprefixed tag format that may appear in old content but must not populate canonical production outputs.
- **Mirrored Source PDF**: A source PDF copied or linked into the generated Markdown output folder's local `pdf/` subdirectory and referenced by a relative wikilink.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a mixed vault fixture, 100% of tags appearing only in generated index, template, support, hidden, spreadsheet, or sidecar files are absent from rebuilt resume counters.
- **SC-002**: In resume fixtures with skipped outputs, every eligible generated output contributes to counters exactly once, with zero duplicate counts from preflight-plus-skip handling.
- **SC-003**: In substantive document fixtures, 100% of successful outputs include a `## Tags` section with at least three justified canonical conceptual tag paths.
- **SC-004**: In substantive document fixtures with missing, empty, or undersized conceptual tags, 100% of affected documents fail with an explicit tagging-quality error before incomplete output is accepted.
- **SC-005**: In administrative-stub fixtures, 100% of empty conceptual tag acceptances are explained by deterministic non-substantive classification.
- **SC-006**: In indexing and spreadsheet export fixtures, 0 obsolete unprefixed tags populate canonical production columns.
- **SC-007**: In masked metadata runs, 0 non-matching Markdown files and 0 `.filtered.md` sidecars are enriched.
- **SC-008**: In dry-run fixtures, filesystem comparison before and after the run shows 0 created, modified, copied, linked, or updated output artifacts.
- **SC-009**: In hierarchical tag fixtures, valid generated tags such as `#Tags/WINTEX/73` produce no malformed-tag warning and populate canonical conceptual tag data with the full path preserved.
- **SC-010**: In nested PDF mirroring fixtures, each generated Markdown file's source PDF is mirrored to that file's local `pdf/` subdirectory, for example `.../1973/pdf/NPG-D(73)11_FRE.pdf`, with a relative `[[pdf/...]]` source link.

## Assumptions

- The current canonical tag model, metadata command, finalization flow, taxonomy, and useful-tags vocabulary remain the authoritative product surface.
- This feature corrects inconsistent use of existing behaviour rather than adding new user-facing commands or alternative models.
- Generated document eligibility can be aligned with the existing interlinking and finalization document-scan behaviour.
- Existing output format expectations, including canonical sections and spreadsheet/index consumers, remain in scope for regression testing.
- Safety options that remain visible to users must behave according to their plain-language meaning even if some mirroring behaviour is preserved for compatibility.
- Source PDF mirroring is part of source-tree mirroring compatibility, but the compatible layout is per generated Markdown folder rather than a single output-root `pdf/` directory.
