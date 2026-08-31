# Tasks: Normalize Qwen 3.8 OCR Output

**Input**: Design documents from `/specs/037-qwen38-ocr-cleanup/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/ocr-output.md, quickstart.md

**Tests**: The specification and quickstart require unit, integration, regression, and coverage validation. Test tasks precede their corresponding implementation tasks.

**Organization**: Tasks are grouped by user story so each behavior can be implemented and validated as a stable increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it affects a different file and has no dependency on another incomplete parallel task.
- **[Story]**: Maps the task to a user story from spec.md.
- Every task names the exact file it changes or validates.

## Path Conventions

- Production code: `archivatorium/`
- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- Feature documentation: `specs/037-qwen38-ocr-cleanup/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the existing OCR pipeline is stable before introducing the shared normalization boundary.

- [X] T001 Run the focused baseline suite for `tests/unit/test_ocr_engine.py` and `tests/integration/test_ocr_cli.py` using `.venv/bin/python -m pytest`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish one model-independent response-normalization boundary used by User Stories 1 and 2 without changing current output.

**⚠️ CRITICAL**: Complete this phase before beginning any user story implementation.

- [X] T002 Add regression tests proving unchanged plain responses pass through every OCR mode at the `ocr_single_page` boundary in `tests/unit/test_ocr_engine.py`
- [X] T003 Introduce a typed identity `normalize_ocr_response` function and call it for every successful response in `OCREngine.ocr_single_page` in `archivatorium/ocr_engine.py`

**Checkpoint**: Every successful OCR response crosses one tested cleanup seam, while request shapes and returned plain text remain unchanged.

---

## Phase 3: User Story 1 - Remove leaked reasoning from OCR text (Priority: P1) 🎯 MVP

**Goal**: Discard every character through the final exact `</think>` marker and remove only the leading blank separators that follow it.

**Independent Test**: Supply responses with adjacent, standalone, repeated, beginning, ending, and absent markers; verify direct return values, previous-page context, and saved Markdown contain only content after the final marker.

### Tests for User Story 1

> **NOTE: Write these tests first and verify they fail before implementing marker cleanup.**

- [X] T004 [P] [US1] Add parameterized final-marker, separator-line, empty-suffix, no-marker, and normalized previous-page-context tests in `tests/unit/test_ocr_engine.py`
- [X] T005 [P] [US1] Add an end-to-end CLI test proving reasoning text and the final `</think>` marker are absent from saved Markdown in `tests/integration/test_ocr_cli.py`

### Implementation for User Story 1

- [X] T006 [US1] Implement exact case-sensitive final-marker partitioning and post-marker leading-blank-line removal in `normalize_ocr_response` in `archivatorium/ocr_engine.py`

**Checkpoint**: User Story 1 passes independently for direct page recognition, contextual multipage recognition, and CLI persistence.

---

## Phase 4: User Story 2 - Remove shared top-level indentation (Priority: P2)

**Goal**: Remove only the common leading ASCII-space margin from nonblank OCR lines while preserving relative indentation, blank lines, and ambiguous tab indentation.

**Independent Test**: Normalize lines indented by four and eight spaces and verify they become zero and four spaces; also verify unindented, tab-indented, mixed tab/space, blank-only, LF, CRLF, and trailing-newline cases.

### Tests for User Story 2

> **NOTE: Write these tests first and verify they fail before implementing dedenting.**

- [X] T007 [P] [US2] Add parameterized shared-margin, relative-indent, blank-line, unindented, tab, mixed-whitespace, empty, LF, CRLF, and trailing-newline tests in `tests/unit/test_ocr_engine.py`
- [X] T008 [P] [US2] Add an end-to-end CLI test proving saved Markdown removes a four-space top-level margin while retaining four spaces of nested indentation in `tests/integration/test_ocr_cli.py`

### Implementation for User Story 2

- [X] T009 [US2] Extend `normalize_ocr_response` with minimum common ASCII-space removal and whole-response tab safeguards in `archivatorium/ocr_engine.py`

**Checkpoint**: User Stories 1 and 2 produce clean page text in the required order: reasoning prefix removal, separator cleanup, then safe shared-margin removal.

---

## Phase 5: User Story 3 - Observe average OCR throughput (Priority: P3)

**Goal**: Log one stable per-PDF timing summary containing distinct attempted-page count, total elapsed seconds, and average seconds per attempted page.

**Independent Test**: Control monotonic time for successful, retried, failed, resumed, fully skipped, and zero-page runs; verify each non-skipped page is counted once, retry/failure time is included, and zero attempts report `unavailable`.

### Tests for User Story 3

> **NOTE: Write these tests first and verify they fail before implementing run metrics.**

- [X] T010 [P] [US3] Add deterministic unit tests for positive averages, three-decimal formatting, retry counting, failure-path logging, resume skips, and zero-attempt runs in `tests/unit/test_ocr_engine.py`
- [X] T011 [P] [US3] Add a CLI integration assertion for the visible `attempted_pages`, `total_seconds`, and `average_seconds_per_page` log fields in `tests/integration/test_ocr_cli.py`

### Implementation for User Story 3

- [X] T012 [US3] Measure the complete `OCREngine.run_ocr` invocation with `time.perf_counter`, count each non-skipped page once before rendering, and emit the stable INFO summary from `finally` in `archivatorium/ocr_engine.py`

**Checkpoint**: All user stories are functional, and failures or zero-attempt runs cannot suppress or break the timing summary.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the combined behavior, performance constraints, and constitutional quality gates.

- [X] T013 Run the mocked automated scenarios in `specs/037-qwen38-ocr-cleanup/quickstart.md` and verify its manual command expectations against `specs/037-qwen38-ocr-cleanup/contracts/ocr-output.md` without requiring archival data or a live model
- [X] T014 Run `ruff check .`, `ruff format --check .`, `flake8`, `mypy .`, the full pytest suite, and coverage reporting using the configurations in `pyproject.toml` and `.flake8`

Validation note: Feature-owned Ruff formatting and Flake8 checks pass, as do repository-wide Ruff lint, MyPy, pytest, and coverage. Repository-wide Ruff formatting also reports four pre-existing untracked Spec Kit helper scripts, and repository-wide Flake8 reports the pre-existing `CCR001` complexity finding in `archivatorium/services/interlinking_service.py`; neither unrelated area was modified by this feature.

---

## Phase 7: Command-Wide Throughput Follow-Up

**Purpose**: Preserve the per-PDF summary while adding overall performance measured from OCR command entry across every processed PDF.

- [X] T015 Add CLI integration coverage for one-PDF, multi-PDF, and zero-attempt command-wide timing in `tests/integration/test_ocr_cli.py`
- [X] T016 Expose each `OCREngine.run_ocr` attempted-page count without changing its string return contract in `archivatorium/ocr_engine.py`
- [X] T017 Measure the outer OCR command lifecycle, aggregate attempted pages across successful and failed PDF runs, and emit the overall INFO summary from `finally` in `archivatorium/cli.py`
- [X] T018 Backpropagate command-wide timing behavior into `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/ocr-output.md`, and `quickstart.md`

Validation note: The full suite passes with 321 tests and 90% application coverage. Feature-owned Ruff, formatting, Flake8, and repository-wide MyPy pass. Repository-wide formatting still reports five unrelated pre-existing test files, while repository-wide Flake8 reports two trailing-blank-line findings in those files and the pre-existing `CCR001` finding in `interlinking_service.py`.

### Cumulative Visibility Follow-Up

- [X] T019 Add CLI integration coverage proving command-start averages appear after each completed PDF in `tests/integration/test_ocr_cli.py`
- [X] T020 Emit cumulative command timing after every PDF while retaining the final overall summary in `archivatorium/cli.py`
- [X] T021 Backpropagate active-batch timing visibility into Feature 037 design artifacts and validate the focused timing scenarios

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Starts immediately and establishes the regression baseline.
- **Foundational (Phase 2)**: Depends on T001 and blocks all story implementation.
- **User Story 1 (Phase 3)**: Depends on T002-T003; delivers the MVP.
- **User Story 2 (Phase 4)**: Depends on T002-T003. It is behaviorally independent from US1, but T009 must be serialized with T006 because both edit the same function.
- **User Story 3 (Phase 5)**: Depends on T001 and the existing engine only. T012 must be serialized with T006 and T009 because all edit `archivatorium/ocr_engine.py`.
- **Polish (Phase 6)**: Depends on all selected story phases.
- **Command-Wide Throughput Follow-Up (Phase 7)**: Depends on the per-PDF metrics from T012 and preserves their stable log contract.

### User Story Dependencies

```text
T001 Baseline
  └── T002 Tests for shared boundary
      └── T003 Shared normalization boundary
          ├── US1: T004 + T005 -> T006
          ├── US2: T007 + T008 -> T009
          └── US3: T010 + T011 -> T012

US1, US2, and US3 are independently testable after T003.
Production edits T006, T009, and T012 are serialized to avoid file conflicts.
All completed stories -> T013 -> T014
```

### Within Each User Story

- Write the unit and integration tests first and confirm they fail for the missing behavior.
- Complete the story's single production implementation task.
- Run that story's focused tests before marking its checkpoint complete.
- Commit each completed task or cohesive test/implementation increment without staging unrelated files.

### Parallel Opportunities

- T004 and T005 can run in parallel because they modify separate test files.
- T007 and T008 can run in parallel because they modify separate test files.
- T010 and T011 can run in parallel because they modify separate test files.
- Test design for different user stories can proceed in parallel after T003, but changes to the shared unit-test file must be coordinated.
- T006, T009, and T012 are never parallel because they all modify `archivatorium/ocr_engine.py`.

---

## Parallel Examples

### User Story 1

```text
Task T004: Add marker-boundary unit tests in tests/unit/test_ocr_engine.py
Task T005: Add persisted-output integration test in tests/integration/test_ocr_cli.py
```

### User Story 2

```text
Task T007: Add shared-indentation unit tests in tests/unit/test_ocr_engine.py
Task T008: Add relative-indentation integration test in tests/integration/test_ocr_cli.py
```

### User Story 3

```text
Task T010: Add deterministic run-metrics unit tests in tests/unit/test_ocr_engine.py
Task T011: Add visible timing-log integration assertion in tests/integration/test_ocr_cli.py
```

---

## Implementation Strategy

### MVP First

1. Complete T001-T003 to establish the shared cleanup boundary.
2. Complete T004-T006 for User Story 1.
3. Run the US1 unit and integration tests and verify saved content contains no leaked reasoning.
4. Commit the stable MVP before extending indentation or metrics behavior.

### Incremental Delivery

1. **Foundation**: Baseline plus one model-independent normalization seam.
2. **US1 MVP**: Remove reasoning through the final marker.
3. **US2**: Add safe shared-margin removal without changing marker behavior.
4. **US3**: Add per-PDF throughput logging without changing text output.
5. **Polish**: Validate the combined contract and all constitutional gates.

### Parallel Team Strategy

1. Complete T001-T003 sequentially.
2. Prepare each story's unit and integration tests in separate coordinated changes.
3. Implement T006, T009, and T012 sequentially in priority order to avoid conflicts in `archivatorium/ocr_engine.py`.
4. Run T013-T014 after all selected stories are integrated.

---

## Notes

- `[P]` marks only tasks that touch different files and have no incomplete dependency.
- `[US1]`, `[US2]`, and `[US3]` provide traceability to the specification.
- Tests precede implementation and must demonstrate the missing behavior before production changes.
- No task changes the default model, OCR modes, request construction, CLI arguments, output naming, retry policy, or resume semantics.
- Real documents and model outputs remain outside version control.
