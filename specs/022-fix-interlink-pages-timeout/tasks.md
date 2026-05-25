# Tasks: fix-interlink-pages-timeout

**Input**: Design documents from `/specs/022-fix-interlink-pages-timeout/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup

**Purpose**: Project initialization and basic structure

- [x] T001 [P] Create initial `topics/unifications.yaml` with Staff Group and Study rules

---

## Phase 2: Foundational

**Purpose**: Core infrastructure for new normalization logic

- [x] T002 [P] Create `tests/unit/test_normalization_rules.py` to verify YAML loading and regex logic
- [x] T003 Implement YAML rule loading in `ocrpolish/services/interlinking_service.py`
- [x] T003b Update `InterlinkingService` to accept a custom unifications path in `ocrpolish/services/interlinking_service.py`
- [x] T003c Add `--unifications` option to `interlink` command in `ocrpolish/cli.py`
- [x] T004 Update `InterlinkingService.normalize_code` in `ocrpolish/services/interlinking_service.py` to apply YAML rules globally

**Checkpoint**: Foundation ready - rules are being applied to archive codes.

---

## Phase 3: User Story 1 - Interlink Unification (Priority: P1) 🎯 MVP

**Goal**: Unify (SG), (Staff Group), etc., and Study variations during interlinking

**Independent Test**: Run `ocrpolish interlink` on a vault with variant codes (e.g., Staff Group vs SG) and verify they are linked correctly.

### Implementation for User Story 1

- [x] T005 [P] [US1] Create `tests/integration/test_interlink_unification.py` with documents using variant codes
- [x] T006 [US1] Ensure `InterlinkingService.discover` uses the updated `normalize_code` in `ocrpolish/services/interlinking_service.py`
- [x] T007 [US1] Ensure `InterlinkingService.resolve_link` uses the updated `normalize_code` in `ocrpolish/services/interlinking_service.py`

**Checkpoint**: User Story 1 complete - vault documents with naming variations are correctly interlinked.

---

## Phase 4: User Story 2 - Page Counting Accuracy (Priority: P2)

**Goal**: Calculate pages based on `# Page X` header count

**Independent Test**: Verify that a document with non-sequential page headers (e.g., 1, 2, 5) reports `3` pages.

### Implementation for User Story 2

- [x] T008 [P] [US2] Update `tests/unit/test_metadata_utils.py` to test header count logic with non-sequential numbers
- [x] T009 [US2] Update `extract_last_page_header` (or rename to `extract_page_count_from_headers`) in `ocrpolish/utils/metadata.py`
- [x] T010 [US2] Update `MetadataProcessor.process_file` in `ocrpolish/processor_metadata.py` to use the new counting logic

**Checkpoint**: User Story 2 complete - page counting is now based on header occurrences.

---

## Phase 5: User Story 3 - Ollama Timeout Configuration (Priority: P3)

**Goal**: Add configurable 5-minute timeout for Ollama calls

**Independent Test**: Mock a slow Ollama response and verify the client times out after 300 seconds.

### Implementation for User Story 3

- [x] T011 [P] [US3] Create `tests/unit/test_ollama_timeout.py` with mocked slow response
- [x] T012 [US3] Add `OLLAMA_TIMEOUT = 300.0` constant to `ocrpolish/services/ollama_client.py`
- [x] T013 [US3] Pass `timeout` to `ollama.Client` in `OllamaClient.__init__` in `ocrpolish/services/ollama_client.py`

**Checkpoint**: User Story 3 complete - Ollama calls now respect the 5-minute timeout.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and cleanup

- [x] T014 [P] Verify all tests pass including legacy interlinking and metadata tests
- [x] T015 Code cleanup and ensuring type hints are correct in modified files
- [x] T016 Run `ruff check .` and `mypy .` to ensure constitutional compliance

---

## Dependencies & Execution Order

- **Foundational (Phase 2)** MUST be complete before **User Story 1** (as it provides the core logic).
- **User Story 2** and **User Story 3** are independent and can be done in parallel or in any order after Phase 1.
- **Polish (Phase 6)** depends on all user stories.

---

## Implementation Strategy

### MVP First (US1)
1. Phase 1 & 2 (Rules setup and implementation)
2. Phase 3 (Unification verification)

### Parallel Opportunities
- T002, T005, T008, T011 (Test writing) can all start in parallel.
- T012, T013 (Timeout config) is independent of interlinking logic.
