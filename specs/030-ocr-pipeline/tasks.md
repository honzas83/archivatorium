# Tasks: OCR Pipeline Integration

**Input**: Design documents from `/specs/030-ocr-pipeline/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are required per project principles (pytest coverage).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Configure core dependencies (`pypdf2`, `pdf2image`, `httpx`) in `pyproject.toml`
- [x] T002 Configure `mypy` overrides for newly added libraries in `pyproject.toml`
- [x] T003 [P] Document developer prerequisites (such as `poppler` install) in `specs/030-ocr-pipeline/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Define Ollama Client connection and initialization wrapper in `ocrpolish/ocr_engine.py`
- [x] T005 [P] Implement basic PDF counting and rendering wrapper in `ocrpolish/ocr_engine.py`
- [x] T006 [P] Create initial shell class and helper structure for markdown page parsing in `ocrpolish/markdown_parser.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Process Directory of PDFs (Priority: P1) 🎯 MVP

**Goal**: Process all PDFs in an input directory recursively, rendering pages, running VLM, and saving them to the output directory.

**Independent Test**: Run `ocrpolish ocr` on `data/test_pdfs` and verify a mirrored `.md` exists with layout-retaining text and sequential `# Page {i}` headings.

### Implementation for User Story 1

- [x] T007 [P] [US1] Create unit tests verifying the single page VLM OCR call in `tests/unit/test_ocr_engine.py`
- [x] T008 [US1] Implement single page OCR API invocation with standard prompts in `ocrpolish/ocr_engine.py`
- [x] T009 [US1] Add the click options and parameters for the `ocr` subcommand in `ocrpolish/cli.py`
- [x] T010 [US1] Implement execution loop that converts PDF, transcribes pages sequentially, joins with markers, and saves to file in `ocrpolish/ocr_engine.py`
- [x] T011 [P] [US1] Add integration test for directory processing and output mirroring in `tests/integration/test_ocr_cli.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Resilient Interruption and Missing Page Recovery (Priority: P1)

**Goal**: Parse existing outputs, validate page completion, and re-process only missing/non-recognized pages using previous page text context.

**Independent Test**: Delete the text of page 2 in an output Markdown. Re-run `ocrpolish ocr` and verify only page 2 is re-processed, utilizing page 1's context.

### Implementation for User Story 2

- [x] T012 [P] [US2] Create unit tests verifying markdown splitting, mapping, and page state parsing in `tests/unit/test_markdown_parser.py`
- [x] T013 [US2] Implement markdown parser to scan file and yield a structured dictionary of page numbers to page contents in `ocrpolish/markdown_parser.py`
- [x] T014 [US2] Implement missing-page detection and previous-page context extraction logic in `ocrpolish/ocr_engine.py`
- [x] T015 [US2] Implement sequential merging and updating of updated pages back into the target Markdown file in `ocrpolish/ocr_engine.py`
- [x] T016 [P] [US2] Add integration test verifying recovery, context ingestion, and update consistency in `tests/unit/test_ocr_engine.py`

**Checkpoint**: User Story 2 is fully complete and validated.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T017 Add click progress bar, verbose logs, and visual feedback for processed files in `ocrpolish/cli.py`
- [x] T018 Run validation steps manually per `specs/030-ocr-pipeline/quickstart.md`
- [x] T019 [P] Run codebase linting, formatting, and type-checks (`ruff check .`, `ruff format .`, `mypy .`)
- [x] T020 [P] Run pytest coverage reporting and verify all tests pass with high coverage (`coverage run -m pytest`)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational phase completion.
  - User Story 1 (US1) is implemented first to build the base pipeline.
  - User Story 2 (US2) builds upon the pipeline from US1.
- **Polish (Final Phase)**: Depends on all user stories being complete.

### User Story Dependencies

- **User Story 1 (US1)**: Can start after Foundational (Phase 2) - No dependencies on other stories.
- **User Story 2 (US2)**: Depends on US1's basic engine for reading and rendering pages.

### Within Each User Story

- Unit tests written to verify core parser and API logic.
- Engine methods implemented before CLI command binding.
- Core pipeline complete before refinement and validation.

### Parallel Opportunities

- Setup tasks (T001, T002, T003) can run in parallel.
- Foundational tasks (T005, T006) can run in parallel.
- User Story 1 tests (T007) and CLI integration (T009) can run in parallel once engine wrapper is sketched out.
- User Story 2 parser unit tests (T012) and context extraction integration tests (T016) can be parallelized.
- Quality gates (T019, T020) in the Polish phase can run in parallel.

---

## Parallel Example: User Story 1

```bash
# Launch test and cli tasks in parallel:
Task: "Create unit tests verifying the single page VLM OCR call in tests/test_ocr_engine.py"
Task: "Add the click options and parameters for the ocr subcommand in ocrpolish/cli.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories).
3. Complete Phase 3: User Story 1.
4. **STOP and VALIDATE**: Test User Story 1 independently.

### Incremental Delivery

1. Complete Setup + Foundational -> Foundation ready.
2. Add User Story 1 -> Test independently (MVP!).
3. Add User Story 2 -> Test independently with page deletions.
4. Run validation and enforce quality gates.

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
