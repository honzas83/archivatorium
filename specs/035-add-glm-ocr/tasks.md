---

description: "Dependency-ordered implementation tasks for GLM OCR mode"
---

# Tasks: Add GLM OCR Mode

**Input**: Design documents from `specs/035-add-glm-ocr/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/cli.md](contracts/cli.md), [quickstart.md](quickstart.md)

**Tests**: Included because the specification defines independent test scenarios and requires exact request, isolation, override, and backward-compatibility validation.

**Organization**: Tasks are grouped by user story. P1 stories are ordered US1 then US4, followed by US2 (P2) and US3 (P3).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with adjacent tasks because it changes different files and does not depend on their unfinished work.
- **[Story]**: Maps the task to its original user story identifier from [spec.md](spec.md).
- Every task names the exact file or files it changes or validates.

## Phase 1: Setup (Shared Test Infrastructure)

**Purpose**: Prepare reusable mocked API and filesystem fixtures without changing production behavior.

- [X] T001 Add reusable mocked Ollama chat responses, client-call capture helpers, and temporary OCR directory/PDF fixtures in tests/conftest.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define the shared typed configuration model required by every story.

**⚠️ CRITICAL**: No user story implementation begins until this phase is complete.

- [X] T002 Define immutable OCRModeProfile and InferenceOverrides value objects, standard-mode resolution, and programmatic validation scaffolding in archivatorium/ocr_engine.py

**Checkpoint**: The engine can represent standard and GLM behavior without placing model selection inside a mode profile.

---

## Phase 3: User Story 1 - Run OCR in GLM Mode (Priority: P1) 🎯 Functional MVP

**Goal**: `--mode glm` sends the native prompt, disables thinking through the remote API contract, applies the six GLM defaults, and recognizes every page without neighboring OCR context.

**Independent Test**: Run the focused US1 tests for a multipage document plus resume and retry cases; every API call must contain one `Text Recognition:` user message, `think=False`, all six defaults, and no text from another page.

### Tests for User Story 1

> Write these tests first and confirm they fail before implementing the story.

- [X] T003 [P] [US1] Add exact GLM request, multipage isolation, resumed-page isolation, and retry-request identity tests in tests/unit/test_ocr_engine.py
- [X] T004 [P] [US1] Add an end-to-end CLI test for `ocr --mode glm` with mocked rendering and remote API calls in tests/integration/test_ocr_cli.py

### Implementation for User Story 1

- [X] T005 [US1] Implement the GLM profile and `/api/chat` request builder with one `Text Recognition:` image message, top-level `think=False`, existing `num_ctx`, and the required defaults in archivatorium/ocr_engine.py
- [X] T006 [US1] Enforce GLM page-context suppression in both OCREngine.run_ocr and OCREngine.ocr_single_page while preserving identical isolated payloads across retries in archivatorium/ocr_engine.py
- [X] T007 [US1] Add optional `--mode glm` parsing and propagate the selected mode into OCREngine without changing positional arguments in archivatorium/cli.py
- [X] T008 [US1] Run and pass the US1 scenarios in tests/unit/test_ocr_engine.py and tests/integration/test_ocr_cli.py

**Checkpoint**: GLM mode is functional for initial, multipage, resumed, and retried recognition and is independently demonstrable.

---

## Phase 4: User Story 4 - Preserve Existing OCR Behavior (Priority: P1) 🚦 Release Gate

**Goal**: Commands that omit `--mode` and inference overrides preserve the existing request, context, model default, traversal, resume, retry, and output behavior; unsupported modes fail before processing.

**Independent Test**: Compare captured no-mode requests and outputs with the pre-feature baseline, verify prior-page context remains present on resume, and verify an unsupported mode exits before client construction or page rendering.

### Tests for User Story 4

> Write these regression tests first and confirm any compatibility break fails before implementation is finalized.

- [X] T009 [P] [US4] Add exact standard system/user message, options, absent-thinking-field, previous-page context, retry, resume, and output-order regression tests in tests/unit/test_ocr_engine.py
- [X] T010 [P] [US4] Add no-mode CLI compatibility and unsupported-mode early-rejection tests in tests/integration/test_ocr_cli.py

### Implementation for User Story 4

- [X] T011 [US4] Make omitted and explicit standard mode reproduce the existing request kwargs, prompts, num_ctx/num_predict values, and context flow without adding `think` or sampling keys in archivatorium/ocr_engine.py
- [X] T012 [US4] Preserve `INPUT_DIR OUTPUT_DIR`, the current `--model` default, recursive discovery, and Click exit semantics while accepting only standard and glm modes in archivatorium/cli.py
- [X] T013 [US4] Run and pass the standard OCR regression scenarios in tests/unit/test_ocr_engine.py and tests/integration/test_ocr_cli.py

**Checkpoint**: Both P1 stories pass; the feature is safe to release without changing existing no-mode workflows.

---

## Phase 5: User Story 2 - Select Model Independently (Priority: P2)

**Goal**: `--model` remains the only selector for the remote model, whether mode is omitted or set to `glm`.

**Independent Test**: Run GLM mode once with the existing default model and once with a custom model; captured requests must use the expected model while GLM prompt, defaults, thinking, and context policy remain identical.

### Tests for User Story 2

> Write these tests first and confirm they fail if a mode profile supplies or replaces a model.

- [X] T014 [P] [US2] Add engine tests proving mode profiles contain no model and preserve default and explicit model values in tests/unit/test_ocr_engine.py
- [X] T015 [P] [US2] Add CLI tests for default-model and custom-`--model` GLM invocations in tests/integration/test_ocr_cli.py

### Implementation for User Story 2

- [X] T016 [US2] Keep model resolution exclusively in the existing CLI-to-OCREngine path and remove any mode-to-model coupling in archivatorium/cli.py and archivatorium/ocr_engine.py
- [X] T017 [US2] Run and pass model-independence scenarios in tests/unit/test_ocr_engine.py and tests/integration/test_ocr_cli.py

**Checkpoint**: Users can combine GLM behavior with any explicitly selected remote model without mode-side substitution.

---

## Phase 6: User Story 3 - Override GLM Inference Defaults (Priority: P3)

**Goal**: Six optional CLI parameters override only their matching mode defaults, preserve valid zero values, and reject invalid input before OCR processing.

**Independent Test**: Parameterize each option individually and all options together; verify exact effective `options`, unchanged unspecified defaults, zero preservation, documented ranges, and early rejection without API or rendering calls.

### Tests for User Story 3

> Write these tests first and confirm they fail before override merging and validation are implemented.

- [X] T018 [P] [US3] Add parameterized default, single-override, all-overrides, explicit-zero, `num_predict=-1`, and invalid programmatic-value tests in tests/unit/test_ocr_engine.py
- [X] T019 [P] [US3] Add CLI propagation and range-rejection tests for `--temperature`, `--top-p`, `--top-k`, `--repeat-penalty`, `--repeat-last-n`, and `--num-predict` in tests/integration/test_ocr_cli.py

### Implementation for User Story 3

- [X] T020 [US3] Implement profile-default plus non-None override merging and validate temperature, top_p, top_k, repeat_penalty, repeat_last_n, and num_predict in archivatorium/ocr_engine.py
- [X] T021 [US3] Add the six optional Click parameters with documented ranges and pass only explicit values to OCREngine in archivatorium/cli.py
- [X] T022 [US3] Run and pass inference-default, override-precedence, boundary-value, and invalid-input scenarios in tests/unit/test_ocr_engine.py and tests/integration/test_ocr_cli.py

**Checkpoint**: All four user stories are independently functional and their focused tests pass.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Align public documentation and complete constitutional validation.

- [X] T023 [P] Document `--mode glm`, the remote Ollama 0.9.0+ API prerequisite, independent `--model`, all inference options, defaults, and examples in README.md
- [X] T024 [P] Reconcile implemented CLI help, request shape, and validation commands with specs/035-add-glm-ocr/contracts/cli.md and specs/035-add-glm-ocr/quickstart.md
- [X] T025 Run ruff, formatting, flake8 complexity, mypy, pytest, and coverage gates configured by pyproject.toml; resolve feature-related findings in archivatorium/cli.py, archivatorium/ocr_engine.py, tests/unit/test_ocr_engine.py, and tests/integration/test_ocr_cli.py
- [X] T026 Execute every automated and manual-safe scenario in specs/035-add-glm-ocr/quickstart.md and record any necessary corrections in specs/035-add-glm-ocr/quickstart.md

---

## Phase 8: Long-Window Repetition Prevention Extension

**Purpose**: Prevent GLM-OCR from repeating multi-line passages that exceed the ordinary short repetition lookback.

- [X] T027 [US3] Backpropagate the `repeat_last_n=512` GLM default, CLI override semantics, and validation range into spec.md, plan.md, research.md, data-model.md, contracts/cli.md, and quickstart.md
- [X] T028 [US3] Add failing unit tests for the GLM default, explicit `repeat_last_n` overrides, valid `-1`/`0` boundaries, and invalid values in tests/unit/test_ocr_engine.py
- [X] T029 [US3] Add failing CLI tests for `--repeat-last-n` propagation and early range rejection in tests/integration/test_ocr_cli.py
- [X] T030 [US3] Implement the GLM `repeat_last_n=512` profile default, override merging, and programmatic validation in archivatorium/ocr_engine.py
- [X] T031 [US3] Add and propagate the validated `--repeat-last-n` Click option in archivatorium/cli.py and document it in README.md
- [X] T032 Run focused OCR tests and project quality gates, then verify the updated CLI help and request contract

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; starts immediately.
- **Foundational (Phase 2)**: Depends on T001 and blocks all user stories.
- **US1 (Phase 3, P1)**: Depends on T002 and delivers the functional GLM MVP.
- **US4 (Phase 4, P1)**: Depends on T002; should follow US1 in a single-developer workflow because both touch the same source/test files. It is the release compatibility gate.
- **US2 (Phase 5, P2)**: Depends on T002 and can be designed independently, but should integrate after both P1 phases to avoid file conflicts.
- **US3 (Phase 6, P3)**: Depends on T002 and GLM default resolution from US1; execute after US1, with the recommended sequence placing it after US2.
- **Polish (Phase 7)**: Depends on all stories selected for release.

### User Story Dependency Graph

```text
Setup T001
    |
Foundation T002
    |----------------------|----------------------|
    v                      v                      v
US1 (P1, functional)   US4 (P1, regression)   US2 (P2, model)
    |                                             |
    +-----------------------> US3 (P3, overrides) |
    |                                             |
    +-------------------------+-------------------+
                              v
                          Polish/Gates
```

- **US1**: No semantic dependency on another story after Foundation.
- **US4**: No semantic dependency on US1, but validates the compatibility of the combined implementation.
- **US2**: No semantic dependency on another story after Foundation; shares integration points with US1.
- **US3**: Depends on the mode-default mechanism delivered by US1.

### Within Each User Story

- Write story tests first and verify that they fail for the missing behavior.
- Implement engine request/configuration behavior before CLI propagation when both are required.
- Run focused story tests before declaring the story checkpoint complete.
- Preserve task-level atomic commits and never stage unrelated existing worktree files.

### Parallel Opportunities

- Within each story, its unit-test task and integration-test task can run in parallel because they modify different files.
- T023 and T024 can run in parallel because README and feature-design documents are separate.
- US4 and US2 are semantically parallel after Foundation, but concurrent implementation is not recommended in one shared worktree because both edit `archivatorium/ocr_engine.py`, `archivatorium/cli.py`, and their tests.
- US3 test design can begin after Foundation, while implementation waits for the US1 default-resolution contract.

---

## Parallel Example: User Story 1

```text
Task T003: Add exact GLM request and isolation tests in tests/unit/test_ocr_engine.py
Task T004: Add CLI GLM journey test in tests/integration/test_ocr_cli.py
```

## Parallel Example: User Story 4

```text
Task T009: Add standard engine regression tests in tests/unit/test_ocr_engine.py
Task T010: Add no-mode and invalid-mode CLI tests in tests/integration/test_ocr_cli.py
```

## Parallel Example: User Story 2

```text
Task T014: Add engine model-independence tests in tests/unit/test_ocr_engine.py
Task T015: Add CLI model-selection tests in tests/integration/test_ocr_cli.py
```

## Parallel Example: User Story 3

```text
Task T018: Add engine inference merge/validation tests in tests/unit/test_ocr_engine.py
Task T019: Add CLI override/range tests in tests/integration/test_ocr_cli.py
```

---

## Implementation Strategy

### Functional MVP First

1. Complete T001-T002 (Setup and Foundation).
2. Complete T003-T008 (US1).
3. Stop and validate GLM mode independently.

### Release-Ready P1 Scope

1. Complete the functional MVP.
2. Complete T009-T013 (US4 backward compatibility).
3. Stop and run both P1 checkpoints before releasing.

### Incremental Delivery

1. Setup + Foundation establish typed mode profiles and reusable tests.
2. US1 adds native independent GLM recognition.
3. US4 proves existing users are unaffected and forms the release gate.
4. US2 proves model/mode independence.
5. US3 adds validated tuning overrides.
6. Polish updates documentation and runs all quality gates.

## Notes

- `[P]` means parallelizable without an unfinished dependency or same-file conflict.
- Story labels preserve the numbering in [spec.md](spec.md), so US4 appears before US2 because its priority is P1.
- The server API contract is authoritative; tasks must not pin behavior to a developer workstation's locally installed Ollama client version.
- No new configuration file, environment variable, Markdown metadata, or model-selection rule is in scope.
- Commit after each task or small logical group, staging only files relevant to this feature.
