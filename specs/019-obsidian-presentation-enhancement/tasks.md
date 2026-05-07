# Tasks: Obsidian Presentation Enhancement

**Input**: Design documents from `/specs/019-obsidian-presentation-enhancement/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Initialize feature development on branch `019-obsidian-presentation-enhancement`
- [x] T002 [P] Verify availability of reference data in `nato_npg_metadata.v4/`
- [x] T003 [P] Configure development environment and verify existing tests pass using `pytest`

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure for metadata and citation enhancements

- [x] T004 [P] Update `format_bibtex_citation` in `ocrpolish/utils/metadata.py` to use `date = {YYYY-MM-DD}` format
- [x] T005 [P] Implement `format_metadata_table` utility in `ocrpolish/utils/metadata.py` using specified icons and field mapping
- [x] T006 [P] Update `generate_tagging_prompt` in `ocrpolish/services/tagging_service.py` to encourage citations in reasons and TitleCase for non-abbreviation uppercase tags
- [x] T007 [P] Create unit tests for BibTeX date format and metadata table formatting in `tests/unit/test_metadata_utils.py`

## Phase 3: User Story 1 - Obsidian Workspace Initialization (Priority: P1) 🎯 MVP

**Goal**: Automatically configure the output vault with specific settings and base files.

**Independent Test**: Run `ocrpolish metadata` and verify `.obsidian/app.json`, `.obsidian/appearance.json`, and `CONTENT.base` exist in the output directory.

### Implementation for User Story 1

- [x] T008 Implement `initialize_vault` function in `ocrpolish/utils/files.py` (or metadata.py) to copy reference files
- [x] T009 Integrate vault initialization trigger into `metadata` command in `ocrpolish/cli.py`
- [x] T010 Add integration test for vault initialization in `tests/integration/test_vault_init.py`

## Phase 4: User Story 2 - Visual Metadata Presentation (Priority: P1)

**Goal**: Insert visual metadata, abstract, and entity callouts into generated markdown.

**Independent Test**: Verify generated markdown files contain `[!info] Metadata`, `[!abstract]`, and `[!citing this document]` callouts.

### Implementation for User Story 2

- [ ] T011 Update `MetadataProcessor.process_file` in `ocrpolish/processor_metadata.py` to generate and insert the `[!info] Metadata` callout at the beginning of the document
- [ ] T012 Update `MetadataProcessor.process_file` in `ocrpolish/processor_metadata.py` to include `Mentioned Entities` and `Categories/Topics` within the `[!abstract]` callout
- [ ] T013 Verify callout order and spacing in `ocrpolish/processor_metadata.py`: Metadata -> Abstract -> Content -> Citation
- [ ] T014 Add regression tests for callout presence and structure in `tests/integration/test_metadata_processor.py`

## Phase 5: User Story 3 - Normalized Topic Citations (Priority: P2)

**Goal**: Consistently format direct citations within topic reasons as `_"citation"_`.

**Independent Test**: Process a file with quotes in topic reasons and verify they are normalized to italicized double quotes.

### Implementation for User Story 3

- [ ] T015 Implement `normalize_topic_citations` helper in `ocrpolish/processor_metadata.py` (or a utility file) using regex to replace quotes with `_"..."_`
- [ ] T016 Integrate citation normalization into the topic processing loop in `MetadataProcessor.process_file`
- [ ] T017 Add unit tests for citation normalization in `tests/unit/test_tagging_normalization.py`

## Phase 6: User Story 4 - Fixed BibTeX Formatting (Priority: P2)

**Goal**: Ensure BibTeX citations match the user-requested structure exactly.

**Independent Test**: Verify BibTeX output in generated files against the user-provided example.

### Implementation for User Story 4

- [x] T018 Refine `format_bibtex_citation` in `ocrpolish/utils/metadata.py` to ensure all fields (author, title, date, note, url, urldate) align with the `@misc` template
- [x] T019 Update `generate_citation_callout` in `ocrpolish/utils/metadata.py` to reflect the refined BibTeX structure
- [x] T020 Verify BibTeX output with an end-to-end processing test in `tests/integration/test_citations_full.py`

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [x] T021 [P] Remove any legacy citation or abstract generation logic that has been superseded
- [x] T022 [P] Perform a final pass with `ruff check .` and `mypy .` to ensure code quality
- [x] T023 Run `specs/019-obsidian-presentation-enhancement/quickstart.md` validation on a sample dataset
- [x] T024 [P] Update `README.md` or existing documentation to reflect new Obsidian features

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup. Blocks User Story implementation.
- **User Stories (Phase 3-6)**: Depend on Foundational phase. Can proceed in parallel where files don't conflict.
- **Polish (Phase 7)**: Depends on all user stories being complete.

### Parallel Opportunities

- T004, T005, T006 can run in parallel in Phase 2.
- T021, T022, T024 can run in parallel in Phase 7.
- User Stories can be implemented largely in parallel once the processor logic is stabilized.

---

## Implementation Strategy

### MVP First (User Story 1 & 2)

1. Complete Setup and Foundational work.
2. Implement Vault Initialization (US1) and Visual Metadata Callouts (US2).
3. **STOP and VALIDATE**: Ensure the output is a functional Obsidian vault with visible metadata.

### Incremental Delivery

1. Foundation -> Vault Init -> Visual Callouts -> Topic Normalization -> BibTeX Fix.
2. Validate each increment with both unit and integration tests.
3. Use `dry-run` during development to verify callout generation without writing large numbers of files.
