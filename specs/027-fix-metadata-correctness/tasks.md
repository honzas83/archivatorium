# Tasks: Metadata Correctness Fixes

**Input**: Design documents from `specs/027-fix-metadata-correctness/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/metadata-correctness.md, quickstart.md

**Tests**: Required by the feature specification and quickstart for resume counters, tagging quality, canonical indexing/export, mask safety, dry-run safety, and full quality gates.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label, used only in user story phases
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish current correctness baselines and identify the exact runtime surfaces before behavioural changes begin.

- [X] T001 Review current generated-document exclusion logic in `ocrpolish/services/interlinking_service.py`
- [X] T002 Review current resume preflight and skipped-output counter handling in `ocrpolish/processor_metadata.py`
- [X] T003 [P] Review current tagging schema, prompt, and aggregation behaviour in `ocrpolish/models/metadata.py` and `ocrpolish/services/tagging_service.py`
- [X] T004 [P] Review current conceptual tag filtering and duplicate suppression in `ocrpolish/utils/nlp.py`
- [X] T005 [P] Review current canonical parser and legacy tag handling in `ocrpolish/utils/tag_parser.py` and `ocrpolish/services/indexing_service.py`
- [X] T006 [P] Review current metadata mask and dry-run orchestration in `ocrpolish/cli.py` and `ocrpolish/processor_metadata.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared helpers and fixtures that all user stories rely on.

**Critical**: No user story implementation should begin until this phase is complete.

- [X] T007 Add reusable mixed-vault fixture builder for generated documents, index pages, support files, templates, hidden folders, and sidecars in `tests/conftest.py`
- [X] T008 [P] Add reusable tagging fixtures for substantive source text, administrative stubs, useful-tags vocabulary, taxonomy, and structured tagging responses in `tests/conftest.py`
- [X] T009 [P] Add reusable filesystem snapshot assertion helper for non-mutating dry-run checks in `tests/conftest.py`
- [X] T010 Define a shared generated-document eligibility helper used by resume and finalization surfaces in `ocrpolish/utils/metadata.py`
- [X] T011 Wire the shared generated-document eligibility helper into discovery exclusions in `ocrpolish/services/interlinking_service.py`
- [X] T012 Add unit tests for generated-document eligibility exclusions and included document outputs in `tests/unit/test_metadata_processor.py`
- [X] T013 Add a compact tagging reuse-hints data structure or helper for conceptual, entity, and topic counters in `ocrpolish/processor_metadata.py`
- [X] T014 Add unit tests for compact tagging reuse-hints construction in `tests/unit/test_processor_counters.py`

**Checkpoint**: Generated-document eligibility, shared fixtures, and compact counter hints are available for story work.

---

## Phase 3: User Story 1 - Resume Counts Only Generated Documents (Priority: P1) MVP

**Goal**: Resume preflight scans only generated document outputs, excludes support artifacts, and counts skipped existing outputs exactly once.

**Independent Test**: Prepare a mixed vault with generated document pages and excluded support artifacts, resume metadata processing, and verify only eligible generated document outputs contribute to counters exactly once.

### Tests for User Story 1

- [X] T015 [P] [US1] Add integration test proving resume preflight ignores `Index - *.md`, support `index.md`, templates, hidden folders, sidecars, and support files in `tests/integration/test_resume_safety.py`
- [X] T016 [P] [US1] Add unit test proving preflight scans only eligible generated document Markdown outputs in `tests/unit/test_processor_counters.py`
- [X] T017 [P] [US1] Add unit test proving skip handling does not re-add a preflight-scanned output in `tests/unit/test_processor_counters.py`
- [X] T018 [P] [US1] Add unit test proving skip handling parses and registers an unscanned skipped output once in `tests/unit/test_processor_counters.py`
- [X] T019 [P] [US1] Add regression test proving tags found only in generated index pages never appear in conceptual, topic, or entity counters in `tests/integration/test_resume_safety.py`

### Implementation for User Story 1

- [X] T020 [US1] Change `preflight_scan` to iterate only eligible generated document Markdown outputs in `ocrpolish/processor_metadata.py`
- [X] T021 [US1] Ensure `preflight_scan` records parsed canonical tags in `scanned_files_tags` before updating counters in `ocrpolish/processor_metadata.py`
- [X] T022 [US1] Update `_skip_existing_output` to use `scanned_files_tags` as the exact-once guard for skipped outputs in `ocrpolish/processor_metadata.py`
- [X] T023 [US1] Normalize output path keys used by preflight, skip handling, and counter updates in `ocrpolish/processor_metadata.py`
- [X] T024 [US1] Run the resume-counter quickstart subset and record any changed validation notes in `specs/027-fix-metadata-correctness/quickstart.md`

**Checkpoint**: User Story 1 is independently functional and protects resumed counters from support-file contamination.

---

## Phase 4: User Story 2 - Substantive Documents Always Receive Conceptual Tags (Priority: P1)

**Goal**: The initial tagging pass requires conceptual tag paths for substantive documents, validates undersized results as quality failures, uses resume hints directly, preserves hierarchical `#Tags/...` values, and preserves useful conceptual vocabulary.

**Independent Test**: Process substantive source fixtures and verify successful outputs include at least three justified conceptual tags; missing, omitted, empty, or undersized conceptual tags fail before incomplete output is accepted.

### Tests for User Story 2

- [X] T025 [P] [US2] Add schema test proving substantive initial tagging requires explicit `conceptual_tags` with at least three items in `tests/unit/test_tagging_service.py`
- [X] T026 [P] [US2] Add prompt test proving mandatory conceptual tag wording replaces permissive `Up to` wording in `tests/unit/test_tagging_service.py`
- [X] T027 [P] [US2] Add validation tests for omitted, empty, and fewer-than-three conceptual tags on substantive text in `tests/unit/test_tagging_service.py`
- [X] T028 [P] [US2] Add tests for deterministic non-substantive administrative-stub classification in `tests/unit/test_tagging_service.py`
- [X] T029 [P] [US2] Add tests proving short substantive policy, organizational, procedural, exercise, command, weapon, and reference texts are substantive in `tests/unit/test_tagging_service.py`
- [X] T030 [P] [US2] Add tests proving resume conceptual counters, entity counters, and topic counters appear as category-specific tagging hints in `tests/unit/test_tagging_service.py`
- [X] T031 [P] [US2] Add duplicate-suppression tests proving generic vocabulary-driven preservation of useful conceptual terms, acronyms, exercise names, and hierarchical conceptual paths in `tests/unit/test_nlp_normalization.py`
- [X] T032 [P] [US2] Add integration test proving a substantive generated output includes a `## Tags` section with at least three `#Tags/...` values in `tests/integration/test_obsidian_metadata.py`
- [X] T033 [P] [US2] Add integration test proving tagging-quality failures do not write incomplete outputs without a `## Tags` section in `tests/integration/test_obsidian_metadata.py`

### Implementation for User Story 2

- [X] T034 [US2] Update tagging result schema descriptions and structured-output expectations for mandatory substantive conceptual tags in `ocrpolish/models/metadata.py`
- [X] T035 [US2] Add deterministic non-substantive administrative-stub classifier for cleaned source text in `ocrpolish/services/tagging_service.py`
- [X] T036 [US2] Replace permissive conceptual tag prompt wording with mandatory substantive-document wording in `ocrpolish/services/tagging_service.py`
- [X] T037 [US2] Add static useful-tags and resume-derived conceptual counters as preferred conceptual vocabulary in tagging prompts in `ocrpolish/services/tagging_service.py`
- [X] T038 [US2] Add entity and subordinate topic reuse hints to tagging prompts without overriding taxonomy choices in `ocrpolish/services/tagging_service.py`
- [X] T039 [US2] Pass compact reuse hints from rebuilt processor counters into `TaggingService.extract_tags` in `ocrpolish/processor_metadata.py`
- [X] T040 [US2] Validate parsed initial tagging results and raise explicit tagging-quality errors for substantive undersized conceptual tags in `ocrpolish/services/tagging_service.py`
- [X] T041 [US2] Ensure `_extract_chunk` does not silently convert tagging-quality failures into empty successful results in `ocrpolish/services/tagging_service.py`
- [X] T042 [US2] Ensure metadata processing propagates tagging-quality failures without writing incomplete generated output in `ocrpolish/processor_metadata.py`
- [X] T043 [US2] Remove any conceptual-tag repair or retry-only fallback path if present in `ocrpolish/services/tagging_service.py`
- [X] T044 [US2] Refine conceptual duplicate suppression to remove exact entity/topic duplicates while preserving substantive conceptual vocabulary without hardcoded domain-term lists in `ocrpolish/utils/nlp.py`
- [X] T045 [US2] Run the tagging-quality quickstart subset and record any changed validation notes in `specs/027-fix-metadata-correctness/quickstart.md`

**Checkpoint**: User Story 2 is independently functional and substantive outputs cannot silently lack conceptual tags.

---

## Phase 5: User Story 3 - Canonical Tags Stay Authoritative End-to-End (Priority: P2)

**Goal**: Production indexing and XLSX export populate canonical views only from canonical tags and never reinterpret obsolete unprefixed tags.

**Independent Test**: Add obsolete tags to generated pages, run indexing and export, and verify obsolete tags do not populate canonical Markdown index or spreadsheet columns while canonical tags still do.

### Tests for User Story 3

- [X] T046 [P] [US3] Add unit test proving `IndexingService.process_file` ignores obsolete unprefixed tags for canonical index entries in `tests/unit/test_indexing_service.py`
- [X] T047 [P] [US3] Add unit test proving Markdown index generation does not use legacy `EntityReference` fallback values in `tests/unit/test_indexing_service.py`
- [X] T048 [P] [US3] Add unit test proving topics YAML index generation ignores obsolete `#Category/...`, `#Topic/...`, and unprefixed topic tags in `tests/unit/test_indexing_topics.py`
- [X] T049 [P] [US3] Add XLSX export test proving obsolete `#State/...`, `#Org/...`, `#City/...`, `#Person/...`, `#Category/...`, and `#Topic/...` values do not populate canonical columns in `tests/unit/test_xlsx_export.py`
- [X] T050 [P] [US3] Add integration test proving interlink finalization exports canonical tags only after document discovery in `tests/integration/test_interlink_cli.py`

### Implementation for User Story 3

- [X] T051 [US3] Remove XLSX export fallback that migrates legacy `EntityReference` values into canonical raw paths in `ocrpolish/services/indexing_service.py`
- [X] T052 [US3] Remove Markdown alphabetical index fallback that populates canonical indices from legacy entity values in `ocrpolish/services/indexing_service.py`
- [X] T053 [US3] Remove topics YAML index fallback that treats `#Category/...`, legacy category tags, or entity values as canonical topics in `ocrpolish/services/indexing_service.py`
- [X] T054 [US3] Ensure interlink-to-index entry construction passes canonical parser output only in `ocrpolish/cli.py`
- [X] T055 [US3] Add optional logging or ignored-tag reporting for obsolete unprefixed tags without populating canonical columns in `ocrpolish/services/indexing_service.py`
- [X] T056 [US3] Run the canonical indexing and XLSX quickstart subset and record any changed validation notes in `specs/027-fix-metadata-correctness/quickstart.md`

**Checkpoint**: User Story 3 is independently functional and production index/export outputs remain canonical-only.

---

## Phase 6: User Story 4 - Masked and Dry Runs Respect User Intent (Priority: P3)

**Goal**: Metadata mask limits enrichment targets and metadata dry-run performs no filesystem mutation.

**Independent Test**: Run metadata with a narrow mask and dry-run over mixed source files, then verify only matching Markdown would be enriched and the filesystem is unchanged during dry-run.

### Tests for User Story 4

- [X] T057 [P] [US4] Add CLI integration test proving `metadata --mask` sends only matching Markdown files to metadata and tagging enrichment in `tests/integration/test_metadata_command.py`
- [X] T058 [P] [US4] Add CLI integration test proving nonmatching Markdown files are not enriched even when mirroring remains enabled in `tests/integration/test_metadata_command.py`
- [X] T059 [P] [US4] Add CLI integration test proving `.filtered.md` sidecars are not enriched by metadata processing in `tests/integration/test_metadata_command.py`
- [X] T060 [P] [US4] Add metadata dry-run integration test proving no vault templates, Markdown outputs, PDFs, non-Markdown mirrors, sidecars, or existing outputs are created or updated in `tests/integration/test_metadata_command.py`
- [X] T061 [P] [US4] Extend existing dry-run regression coverage for filesystem snapshot comparison in `tests/integration/test_dry_run.py`

### Implementation for User Story 4

- [X] T062 [US4] Change metadata CLI file enumeration so only mask-matching Markdown files are enriched in `ocrpolish/cli.py`
- [X] T063 [US4] Preserve intentional nonmatching file mirroring only outside dry-run and without enriching nonmatching Markdown files in `ocrpolish/cli.py`
- [X] T064 [US4] Ensure `.filtered.md` sidecars are excluded from metadata enrichment in both CLI and processor paths in `ocrpolish/cli.py` and `ocrpolish/processor_metadata.py`
- [X] T065 [US4] Make metadata dry-run skip vault template initialization in `ocrpolish/cli.py`
- [X] T066 [US4] Make metadata dry-run skip generated Markdown writes, PDF mirroring, non-Markdown copy or hardlink operations, sidecar writes, and existing output updates in `ocrpolish/cli.py`
- [X] T067 [US4] Add dry-run planned-action reporting for scanned inputs and computed output paths in `ocrpolish/cli.py`
- [X] T068 [US4] Run the metadata mask and dry-run quickstart subset and record any changed validation notes in `specs/027-fix-metadata-correctness/quickstart.md`

**Checkpoint**: User Story 4 is independently functional and metadata safety options match user intent.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation cleanup, and repository hygiene.

- [X] T069 [P] Update README metadata correctness notes for resume, tagging, canonical export, mask, and dry-run behaviour in `README.md`
- [X] T070 [P] Update quickstart validation results and final expected outcomes in `specs/027-fix-metadata-correctness/quickstart.md`
- [X] T071 Run `pytest tests/integration/test_resume_safety.py tests/unit/test_processor_counters.py` and fix regressions in affected `ocrpolish/` and `tests/` files
- [X] T072 Run `pytest tests/unit/test_tagging_service.py tests/unit/test_nlp_normalization.py tests/integration/test_obsidian_metadata.py` and fix regressions in affected `ocrpolish/` and `tests/` files
- [X] T073 Run `pytest tests/unit/test_indexing_service.py tests/unit/test_indexing_topics.py tests/unit/test_xlsx_export.py tests/integration/test_interlink_cli.py` and fix regressions in affected `ocrpolish/` and `tests/` files
- [X] T074 Run `pytest tests/integration/test_metadata_command.py tests/integration/test_dry_run.py tests/unit/test_file_exclusion.py` and fix regressions in affected `ocrpolish/` and `tests/` files
- [X] T075 Run `ruff check .` and fix reported issues in affected `ocrpolish/` and `tests/` files
- [X] T076 Run `ruff format --check .` and apply formatting if needed in affected `ocrpolish/` and `tests/` files
- [X] T077 Run `flake8` and reduce any new complexity issues in affected `ocrpolish/` files
- [X] T078 Run `mypy .` and fix typing issues in affected `ocrpolish/` files
- [X] T079 Run `pytest` and resolve full-suite regressions in affected `ocrpolish/` and `tests/` files
- [X] T080 Run `coverage run -m pytest` and `coverage report` to confirm coverage gates for the feature

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies.
- **Phase 2 Foundational**: Depends on Phase 1 and blocks all user stories.
- **Phase 3 US1**: Depends on Phase 2; delivers MVP resume-counter correctness.
- **Phase 4 US2**: Depends on Phase 2; can run in parallel with US1 after shared eligibility and hint structures are ready, but benefits from US1 counter correctness.
- **Phase 5 US3**: Depends on Phase 2; can run after canonical parser assumptions are confirmed and does not require US1 or US2 implementation.
- **Phase 6 US4**: Depends on Phase 2; can run independently after CLI/process discovery surfaces are reviewed.
- **Phase 7 Polish**: Depends on all selected user stories.

### User Story Dependencies

- **US1 (P1)**: Can start after foundational tasks; suggested MVP.
- **US2 (P1)**: Can start after foundational tasks; uses reuse-hint helper from Phase 2 and gains best data after US1.
- **US3 (P2)**: Can start after foundational tasks; independent of metadata enrichment and resume counting.
- **US4 (P3)**: Can start after foundational tasks; independent of tagging quality and indexing cleanup.

### Parallel Opportunities

- T003-T006 can run in parallel during setup because they inspect different runtime surfaces.
- T007-T009 can run in parallel while T010-T014 establish shared helpers and tests.
- US1 tests T015-T019 can run in parallel before implementation.
- US2 tests T025-T033 can run in parallel across tagging, NLP, and integration files.
- US3 tests T046-T050 can run in parallel across indexing, topics, XLSX, and interlink files.
- US4 tests T057-T061 can run in parallel with coordination in integration files.
- Documentation tasks T069-T070 can run in parallel after behaviour stabilizes.

---

## Parallel Execution Examples

### User Story 1

```text
Task: "T015 [P] [US1] Add integration test proving resume preflight ignores Index - *.md, support index.md, templates, hidden folders, sidecars, and support files in tests/integration/test_resume_safety.py"
Task: "T016 [P] [US1] Add unit test proving preflight scans only eligible generated document Markdown outputs in tests/unit/test_processor_counters.py"
Task: "T019 [P] [US1] Add regression test proving tags found only in generated index pages never appear in conceptual, topic, or entity counters in tests/integration/test_resume_safety.py"
```

### User Story 2

```text
Task: "T025 [P] [US2] Add schema test proving substantive initial tagging requires explicit conceptual_tags with at least three items in tests/unit/test_tagging_service.py"
Task: "T031 [P] [US2] Add duplicate-suppression tests proving generic vocabulary-driven preservation of useful conceptual terms, acronyms, exercise names, and hierarchical conceptual paths in tests/unit/test_nlp_normalization.py"
Task: "T032 [P] [US2] Add integration test proving a substantive generated output includes a ## Tags section with at least three #Tags/... values in tests/integration/test_obsidian_metadata.py"
```

### User Story 3

```text
Task: "T046 [P] [US3] Add unit test proving IndexingService.process_file ignores obsolete unprefixed tags for canonical index entries in tests/unit/test_indexing_service.py"
Task: "T049 [P] [US3] Add XLSX export test proving obsolete #State/..., #Org/..., #City/..., #Person/..., #Category/..., and #Topic/... values do not populate canonical columns in tests/unit/test_xlsx_export.py"
Task: "T050 [P] [US3] Add integration test proving interlink finalization exports canonical tags only after document discovery in tests/integration/test_interlink_cli.py"
```

### User Story 4

```text
Task: "T057 [P] [US4] Add CLI integration test proving metadata --mask sends only matching Markdown files to metadata and tagging enrichment in tests/integration/test_metadata_command.py"
Task: "T059 [P] [US4] Add CLI integration test proving .filtered.md sidecars are not enriched by metadata processing in tests/integration/test_metadata_command.py"
Task: "T060 [P] [US4] Add metadata dry-run integration test proving no vault templates, Markdown outputs, PDFs, non-Markdown mirrors, sidecars, or existing outputs are created or updated in tests/integration/test_metadata_command.py"
```

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate resume-counter correctness with the quickstart subset.
4. Stop and review counter behaviour before relying on resume hints in tagging.

### Incremental Delivery

1. Deliver US1 to make resumed counters trustworthy.
2. Deliver US2 to enforce conceptual tag quality and consume trustworthy hints.
3. Deliver US3 to remove legacy fallback behaviour from index/export.
4. Deliver US4 to make metadata safety options non-surprising.
5. Run Phase 7 quality gates and documentation updates.

### Validation Gates

1. US1 complete when mixed-vault fixtures show only eligible generated document outputs contribute exactly once.
2. US2 complete when substantive documents cannot succeed without at least three conceptual tags and administrative stubs are detected deterministically.
3. US3 complete when obsolete unprefixed tags populate zero canonical index or XLSX columns.
4. US4 complete when mask limits enrichment and dry-run performs zero filesystem mutations.
5. Feature complete when ruff, format check, flake8, mypy, pytest, and coverage gates pass.
