# Tasks: Simplify Metadata Pipeline

**Input**: Design documents from `specs/026-simplify-metadata-pipeline/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/metadata-command.md, quickstart.md

**Tests**: Required by the feature specification for production behaviour, staged processing regressions, flat tagging, and prompt precomputation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label, used only in user story phases
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the current production baseline and identify legacy topic artifacts before runtime changes begin.

- [X] T001 Review current metadata CLI options and PDF mirroring behaviour in `ocrpolish/cli.py`
- [X] T002 Review current source-link, rendering, reconciliation, and counter ingestion behaviour in `ocrpolish/processor_metadata.py`
- [X] T003 [P] Review current flat tagging and prompt construction behaviour in `ocrpolish/services/tagging_service.py`
- [X] T004 [P] Inventory legacy topic extraction imports and tests in `ocrpolish/services/topics_service.py`, `tests/test_topics_service.py`, `tests/unit/test_topics_service_flat.py`, and `tests/evaluate_topic_accuracy.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared test fixtures and pipeline result structures that all user stories need.

**Critical**: No user story work can begin until this phase is complete.

- [X] T005 [P] Add reusable hierarchy and useful-tags fixtures for metadata command tests in `tests/conftest.py`
- [X] T006 [P] Add reusable mocked Ollama metadata/tagging responses for production metadata tests in `tests/conftest.py`
- [X] T007 Define internal pipeline stage result dataclasses or typed records in `ocrpolish/processor_metadata.py`
- [X] T008 Add helper for deriving mirrored PDF output paths and vault-relative PDF source links in `ocrpolish/processor_metadata.py`

**Checkpoint**: Shared fixtures and typed pipeline foundations are ready for story implementation.

---

## Phase 3: User Story 1 - Run the simplified production command (Priority: P1)

**Goal**: The canonical metadata command requires explicit hierarchy/tags files, defaults omitted vault/PDF roots to the output directory, mirrors PDFs into `pdf/`, and writes `[[pdf/<filename>.pdf]]` source links.

**Independent Test**: Run the metadata command with only input directory, output directory, hierarchy file, and tags file; verify output Markdown, mirrored PDF location, and generated source link.

### Tests for User Story 1

- [X] T009 [P] [US1] Add CLI failure tests for missing `--hierarchy-file` and missing `--tags-file` in `tests/integration/test_metadata_command.py`
- [X] T010 [P] [US1] Add CLI success test for the canonical production command without `--vault-root`, `--pdf-dir`, or topic-mode flags in `tests/integration/test_metadata_command.py`
- [X] T011 [P] [US1] Add integration test proving PDFs are mirrored to output `pdf/` and source links are `[[pdf/<filename>.pdf]]` in `tests/integration/test_pdf_subdirectory.py`
- [X] T012 [P] [US1] Add collision or ambiguity coverage for mirrored PDF source links in `tests/integration/test_pdf_subdirectory.py`

### Implementation for User Story 1

- [X] T013 [US1] Make `--hierarchy-file` and `--tags-file` required metadata command options in `ocrpolish/cli.py`
- [X] T014 [US1] Remove the production topic-mode option from the metadata command in `ocrpolish/cli.py`
- [X] T015 [US1] Default effective `vault_root` and `pdf_dir` to `output_dir` when omitted in `ocrpolish/cli.py`
- [X] T016 [US1] Wire `TaggingService` construction as flat production tagging without a caller-selected mode in `ocrpolish/cli.py`
- [X] T017 [US1] Change PDF mirroring in the metadata command to always write source PDFs into the generated `pdf/` layout in `ocrpolish/cli.py`
- [X] T018 [US1] Change metadata source-link generation to derive `[[pdf/<filename>.pdf]]` from the mirrored output layout in `ocrpolish/processor_metadata.py`
- [X] T019 [US1] Preserve Obsidian vault initialization and recursive mirrored source structure while applying the new defaults in `ocrpolish/cli.py`
- [X] T020 [US1] Run the US1 test subset from `quickstart.md` and record any compatibility adjustments in `specs/026-simplify-metadata-pipeline/quickstart.md`

**Checkpoint**: User Story 1 is independently functional and validates the intended production command.

---

## Phase 4: User Story 2 - Use only flat production topic extraction (Priority: P1)

**Goal**: Production metadata processing exposes only the flat tagging path, with obsolete non-flat extraction removed from runtime behaviour and production tests.

**Independent Test**: Search production runtime and tests for legacy non-flat entry points, then run flat tagging production tests.

### Tests for User Story 2

- [X] T021 [P] [US2] Replace legacy production topic extractor tests with flat `TaggingService` coverage in `tests/unit/test_tagging_service.py`
- [X] T022 [P] [US2] Remove or relocate production tests that import `TopicExtractor` from `tests/test_topics_service.py` and `tests/unit/test_topics_service_flat.py`
- [X] T023 [P] [US2] Add regression assertion that the metadata CLI exposes no non-flat topic mode in `tests/integration/test_metadata_command.py`
- [X] T024 [P] [US2] Move or rewrite old topic accuracy evaluation outside the production package test path in `tests/evaluate_topic_accuracy.py`

### Implementation for User Story 2

- [X] T025 [US2] Remove `TopicExtractor` from the production runtime path in `ocrpolish/services/topics_service.py`
- [X] T026 [US2] Remove production-only legacy topic schemas if no runtime code uses them in `ocrpolish/models/topics.py`
- [X] T027 [US2] Ensure metadata processing imports no legacy topic extractor code in `ocrpolish/cli.py` and `ocrpolish/processor_metadata.py`
- [X] T028 [US2] Run `rg -n "TopicExtractor|flat_mode|two-step|CategorySelectionSchema|TopicSelectionSchema" ocrpolish tests` and resolve any remaining production-runtime references

**Checkpoint**: User Story 2 is independently functional and production topic extraction is flat-only.

---

## Phase 5: User Story 3 - Preserve metadata output while exposing pipeline stages (Priority: P2)

**Goal**: `MetadataProcessor.process_file` becomes an explicit internal pipeline with independently testable stages while preserving compatible generated output.

**Independent Test**: Call each stage with controlled inputs/outputs, then compare full processed output for compatibility-critical frontmatter, callout ordering, citations, page counts, mirrored structure, and tag counters.

### Tests for User Story 3

- [X] T029 [P] [US3] Add stage-level tests for source reading and generated-section stripping in `tests/unit/test_metadata_processor.py`
- [X] T030 [P] [US3] Add stage-level tests for document metadata extraction and page-count fallback in `tests/unit/test_metadata_processor.py`
- [X] T031 [P] [US3] Add stage-level tests for generated tag extraction and topic reason normalization in `tests/unit/test_metadata_processor.py`
- [X] T032 [P] [US3] Add stage-level tests for metadata/tag reconciliation and frontmatter rendering in `tests/unit/test_reconciliation.py`
- [X] T033 [P] [US3] Add stage-level tests for callout ordering and citation rendering in `tests/unit/test_metadata_processor.py`
- [X] T034 [P] [US3] Add generated-output tag ingestion and counter regression tests in `tests/unit/test_processor_counters.py`
- [X] T035 [P] [US3] Add full output compatibility regression for mirrored structure, vault initialization, citations, page counts, and interlink-compatible links in `tests/integration/test_obsidian_metadata.py`

### Implementation for User Story 3

- [X] T036 [US3] Extract read-source stage from `process_file` into a testable method in `ocrpolish/processor_metadata.py`
- [X] T037 [US3] Extract parse-and-strip stage using existing frontmatter and generated-section helpers in `ocrpolish/processor_metadata.py`
- [X] T038 [US3] Extract document metadata extraction stage, including first-chunk prompt construction and large-document date fallback, in `ocrpolish/processor_metadata.py`
- [X] T039 [US3] Extract generated tag extraction stage using `TaggingService` in `ocrpolish/processor_metadata.py`
- [X] T040 [US3] Extract metadata/tag reconciliation stage, including source link, citekey, page count, and existing frontmatter rules, in `ocrpolish/processor_metadata.py`
- [X] T041 [US3] Extract frontmatter rendering stage using existing metadata helpers in `ocrpolish/processor_metadata.py`
- [X] T042 [US3] Extract callout rendering stage preserving Metadata, Abstract, body, and Citation ordering in `ocrpolish/processor_metadata.py`
- [X] T043 [US3] Extract write-output stage and generated-output tag ingestion stage in `ocrpolish/processor_metadata.py`
- [X] T044 [US3] Recompose `process_file` as the explicit pipeline orchestrator in `ocrpolish/processor_metadata.py`

**Checkpoint**: User Story 3 is independently functional and pipeline stages can be tested without changing compatible output.

---

## Phase 6: User Story 4 - Avoid repeated static prompt construction (Priority: P3)

**Goal**: `TaggingService` computes flattened taxonomy and static useful-tag prompt sections once during initialization and reuses them for all tagging windows.

**Independent Test**: Process a multi-window document and verify static prompt sections are prepared once per service instance and reused for each window.

### Tests for User Story 4

- [X] T045 [P] [US4] Add initialization test proving taxonomy flattening and YAML serialization happen once in `tests/unit/test_tagging_service.py`
- [X] T046 [P] [US4] Add sliding-window test proving per-window prompts reuse static taxonomy and useful-tag text in `tests/unit/test_tagging_service.py`
- [X] T047 [P] [US4] Add production flat topic format assertion for `Category/Topic` prompts in `tests/unit/test_tagging_service.py`

### Implementation for User Story 4

- [X] T048 [US4] Remove caller-controlled `flat_mode` branching from production prompt generation in `ocrpolish/services/tagging_service.py`
- [X] T049 [US4] Precompute normalized flattened taxonomy and taxonomy prompt text during `TaggingService` initialization in `ocrpolish/services/tagging_service.py`
- [X] T050 [US4] Precompute useful-tag prompt text during `TaggingService` initialization in `ocrpolish/services/tagging_service.py`
- [X] T051 [US4] Update `_generate_tagging_prompt` to reuse static prompt sections and vary only by document excerpt in `ocrpolish/services/tagging_service.py`
- [X] T052 [US4] Verify sliding-window tagging no longer dumps taxonomy YAML or rebuilds static prompt sections per chunk in `ocrpolish/services/tagging_service.py`

**Checkpoint**: User Story 4 is independently functional and prompt construction is precomputed for multi-window tagging.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation cleanup, and repository hygiene.

- [X] T053 [P] Update quickstart validation commands and expected outcomes after implementation in `specs/026-simplify-metadata-pipeline/quickstart.md`
- [X] T054 [P] Update production documentation for the canonical metadata command in `README.md`
- [X] T055 Run focused metadata command, flat tagging, staged processor, and prompt precomputation test subsets from `specs/026-simplify-metadata-pipeline/quickstart.md`
- [X] T056 Run `ruff check .` and fix reported issues in affected `ocrpolish/` and `tests/` files
- [X] T057 Run `ruff format --check .` and apply formatting if needed in affected `ocrpolish/` and `tests/` files
- [X] T058 Run `flake8` and reduce any new complexity issues in `ocrpolish/processor_metadata.py`
- [X] T059 Run `mypy .` and fix typing issues in affected `ocrpolish/` files
- [X] T060 Run `pytest` and resolve regressions in affected `tests/` files
- [X] T061 Run `coverage run -m pytest` and `coverage report` to confirm coverage gates for the feature

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies.
- **Phase 2 Foundational**: Depends on Phase 1 completion and blocks all user stories.
- **Phase 3 US1**: Depends on Phase 2; delivers the MVP command and output-link compatibility.
- **Phase 4 US2**: Depends on Phase 2; can run in parallel with US1 after shared foundations, but final CLI assertions may overlap with US1.
- **Phase 5 US3**: Depends on Phase 2 and should run after US1 decisions for source-link computation are settled.
- **Phase 6 US4**: Depends on Phase 2 and can run in parallel with US3 after flat-only production behaviour is clear.
- **Phase 7 Polish**: Depends on all selected user stories.

### User Story Dependencies

- **US1 (P1)**: No dependency on other stories after foundational tasks. Suggested MVP.
- **US2 (P1)**: No dependency on US1 after foundational tasks, but coordinates with US1 on CLI option removal.
- **US3 (P2)**: Depends on source-link and flat tagging contracts from US1/US2 for final compatibility tests.
- **US4 (P3)**: Depends on flat-only production direction from US2.

### Parallel Opportunities

- T003 and T004 can run in parallel with T001/T002 review work.
- T005 and T006 can run in parallel because both edit shared fixtures but should be merged carefully in `tests/conftest.py`.
- US1 test tasks T009-T012 can run in parallel before US1 implementation.
- US2 test cleanup tasks T021-T024 can run in parallel across separate test/evaluation files.
- US3 stage test tasks T029-T035 can run in parallel across unit and integration files.
- US4 tests T045-T047 can run in parallel in the same file only with coordination, or sequentially if handled by one implementer.
- Documentation tasks T053 and T054 can run in parallel with final quality gates once behaviour is stable.

## Parallel Execution Examples

### User Story 1

```text
Task: "T009 [P] [US1] Add CLI failure tests for missing --hierarchy-file and missing --tags-file in tests/integration/test_metadata_command.py"
Task: "T011 [P] [US1] Add integration test proving PDFs are mirrored to output pdf/ and source links are [[pdf/<filename>.pdf]] in tests/integration/test_pdf_subdirectory.py"
Task: "T012 [P] [US1] Add collision or ambiguity coverage for mirrored PDF source links in tests/integration/test_pdf_subdirectory.py"
```

### User Story 2

```text
Task: "T021 [P] [US2] Replace legacy production topic extractor tests with flat TaggingService coverage in tests/unit/test_tagging_service.py"
Task: "T022 [P] [US2] Remove or relocate production tests that import TopicExtractor from tests/test_topics_service.py and tests/unit/test_topics_service_flat.py"
Task: "T024 [P] [US2] Move or rewrite old topic accuracy evaluation outside the production package test path in tests/evaluate_topic_accuracy.py"
```

### User Story 3

```text
Task: "T029 [P] [US3] Add stage-level tests for source reading and generated-section stripping in tests/unit/test_metadata_processor.py"
Task: "T032 [P] [US3] Add stage-level tests for metadata/tag reconciliation and frontmatter rendering in tests/unit/test_reconciliation.py"
Task: "T034 [P] [US3] Add generated-output tag ingestion and counter regression tests in tests/unit/test_processor_counters.py"
```

### User Story 4

```text
Task: "T045 [P] [US4] Add initialization test proving taxonomy flattening and YAML serialization happen once in tests/unit/test_tagging_service.py"
Task: "T046 [P] [US4] Add sliding-window test proving per-window prompts reuse static taxonomy and useful-tag text in tests/unit/test_tagging_service.py"
Task: "T047 [P] [US4] Add production flat topic format assertion for Category/Topic prompts in tests/unit/test_tagging_service.py"
```

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate the canonical production command, required options, mirrored PDFs, and generated source links.
4. Stop and review compatibility before removing legacy topic runtime paths.

### Incremental Delivery

1. Deliver US1 to stabilize the production command contract.
2. Deliver US2 to remove obsolete topic modes and simplify production behaviour.
3. Deliver US3 to refactor processing internals while preserving observable output.
4. Deliver US4 to reduce repeated static prompt construction.
5. Run Phase 7 quality gates and documentation updates.

### Validation Gates

1. US1 complete when metadata command tests prove required files, defaults, mirrored PDFs, and source links.
2. US2 complete when production runtime/tests no longer expose `TopicExtractor` or non-flat topic mode.
3. US3 complete when stage-level tests and full compatibility regression pass.
4. US4 complete when prompt precomputation tests prove static sections are reused across windows.
5. Feature complete when ruff, format check, flake8, mypy, pytest, and coverage gates pass.
