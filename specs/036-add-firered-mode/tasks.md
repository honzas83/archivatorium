---

description: "Implementation tasks for the FireRed OCR mode"
---

# Tasks: Add FireRed OCR Mode

**Input**: Design documents from `specs/036-add-firered-mode/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/cli.md](contracts/cli.md), [quickstart.md](quickstart.md)

**Tests**: Required. The specification defines acceptance scenarios for the exact FireRed request, page isolation, resume/retry behavior, output continuity, and regression compatibility.

**Organization**: Tasks are grouped by user story so every delivered increment has a clear verification target.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it affects a different file and has no unfinished dependency.
- **[Story]**: User story mapped from [spec.md](spec.md).

## Phase 1: Setup

**Purpose**: Confirm the existing OCR test seams and request-profile baseline before changes.

- [X] T001 Review the existing profile, CLI, and mock request assertions in `archivatorium/ocr_engine.py`, `archivatorium/cli.py`, `tests/unit/test_ocr_engine.py`, and `tests/integration/test_ocr_cli.py` against `specs/036-add-firered-mode/contracts/cli.md`.

---

## Phase 2: Foundational

**Purpose**: No standalone infrastructure is needed. The established OCR mode-profile abstraction, Click command, test fixtures, retry loop, and resume parser are the shared foundation.

**Checkpoint**: Begin user-story work after T001; do not create a new engine, storage schema, configuration store, or command.

---

## Phase 3: User Story 1 - Recognize documents with the FireRed profile (Priority: P1) 🎯 MVP

**Goal**: Let a user select FireRed mode and receive regular Markdown output from a request using exactly the supplied FireRed prompt.

**Independent Test**: Run OCR with `--mode firered` on a mocked single-page PDF and assert one user message, the exact prompt, the page image, the selected model, normal output, and no system or `think` field.

### Tests for User Story 1

- [X] T002 [P] [US1] Add failing exact single-page FireRed request and selected-model assertions to `tests/unit/test_ocr_engine.py`.
- [X] T003 [P] [US1] Add a failing `--mode firered` mocked CLI-to-Markdown output and request-contract test to `tests/integration/test_ocr_cli.py`.

### Implementation for User Story 1

- [X] T004 [US1] Add the exact FireRed prompt constant and immutable `firered` profile with no system prompt, no previous-page context, unchanged thinking behavior, and standard defaults to `archivatorium/ocr_engine.py`.
- [X] T005 [US1] Resolve `firered` to the new profile while retaining standard and GLM resolution unchanged in `archivatorium/ocr_engine.py`.
- [X] T006 [US1] Add `firered` to the `--mode` choice without changing its default or other OCR options in `archivatorium/cli.py`.
- [X] T007 [US1] Run and make the focused FireRed unit and integration assertions pass in `tests/unit/test_ocr_engine.py` and `tests/integration/test_ocr_cli.py`.

**Checkpoint**: A single page can be processed with `--mode firered`; its request contains exactly the required prompt and its transcription remains in the usual output.

---

## Phase 4: User Story 2 - Keep FireRed pages independent (Priority: P1)

**Goal**: Ensure FireRed page recognition remains isolated in multipage runs, resume/missing-page recovery, and retries.

**Independent Test**: Use sentinel text from prior and neighboring pages in mocked multipage, resumed, and retried runs; none may appear in any FireRed request, while the request prompt remains exact.

### Tests for User Story 2

- [X] T008 [US2] Add failing FireRed retry-equivalence, multipage no-neighbor-context, and resumed missing-page isolation tests to `tests/unit/test_ocr_engine.py`.

### Implementation for User Story 2

- [X] T009 [US2] Adjust only `archivatorium/ocr_engine.py` if the isolation tests expose a context leak; preserve the profile-controlled request builder and existing retry/resume/output behavior.
- [X] T010 [US2] Run the FireRed isolation scenarios and make them pass in `tests/unit/test_ocr_engine.py`.

**Checkpoint**: Initial processing, retries, and resumed recognition send no recognized text from any other page.

---

## Phase 5: User Story 3 - Preserve existing OCR modes (Priority: P1)

**Goal**: Keep standard and GLM workflows fully backward compatible while the new mode is opt-in.

**Independent Test**: Run focused tests with mode omitted, `standard`, and `glm`, and verify original request shapes, context policies, and validation behavior remain intact.

### Tests for User Story 3

- [X] T011 [US3] Add or strengthen standard/GLM regression and unsupported-mode-before-processing assertions affected by the expanded choice in `tests/unit/test_ocr_engine.py` and `tests/integration/test_ocr_cli.py`.

### Implementation for User Story 3

- [X] T012 [US3] Correct any compatibility regression in `archivatorium/ocr_engine.py` and `archivatorium/cli.py` without changing standard prompts/context, GLM prompting/isolation, model selection, inference settings, traversal, or output structure.
- [X] T013 [US3] Run the focused standard, GLM, FireRed, and invalid-mode regressions in `tests/unit/test_ocr_engine.py` and `tests/integration/test_ocr_cli.py`.

**Checkpoint**: Standard and GLM tests retain their pre-existing request contracts, and unsupported modes fail before processing.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Document the new public value and execute project quality gates.

- [X] T014 [P] Document `firered` in the OCR mode reference and add a minimal FireRed command example in `README.md`.
- [X] T015 Run the focused validation and all required linting, formatting, typing, test, and coverage commands from `specs/036-add-firered-mode/quickstart.md`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Starts immediately.
- **Foundational (Phase 2)**: Depends on T001; confirms reuse of existing shared infrastructure.
- **US1 (Phase 3)**: Depends on T001 and delivers the MVP profile and public selection.
- **US2 (Phase 4)**: Depends on T004–T007 because the profile must exist before isolation is verified.
- **US3 (Phase 5)**: Depends on T006 and can be completed after US1; run it after US2 for the final combined regression checkpoint.
- **Polish (Phase 6)**: Depends on all desired user-story phases.

### User Story Dependencies

- **US1**: First delivery; no dependency on another story.
- **US2**: Extends the profile delivered in US1 with multipage, resume, and retry validation.
- **US3**: Validates opt-in compatibility after the CLI choice is expanded; it has no new runtime feature dependency beyond US1.

### Parallel Opportunities

- T002 and T003 can run in parallel because they modify different test files.
- T014 can run in parallel with the final test work after the CLI contract is stable.
- No other tasks are marked parallel because they modify the shared OCR engine or the same test modules.

## Parallel Example: User Story 1

```text
Task: "Add failing exact single-page FireRed request and selected-model assertions to tests/unit/test_ocr_engine.py"
Task: "Add a failing --mode firered mocked CLI-to-Markdown output and request-contract test to tests/integration/test_ocr_cli.py"
```

## Implementation Strategy

### MVP First

1. Complete T001–T007.
2. Validate User Story 1 independently with its focused tests.
3. Demonstrate `archivatorium ocr --mode firered` with a mocked single-page document.

### Incremental Delivery

1. Add US1 to establish the profile and CLI choice.
2. Add US2 to prove page isolation through every recovery path.
3. Add US3 to lock down backward compatibility.
4. Update documentation and run all quality gates.

## Notes

- All 15 tasks use the required checkbox, sequential identifier, relevant story label, and exact file path format.
- Keep commits scoped to the task's files; do not stage unrelated dirty-worktree changes.
