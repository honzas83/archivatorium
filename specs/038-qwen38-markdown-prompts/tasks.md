---

description: "Task list for the Qwen 3.8 Markdown OCR mode"
---

# Tasks: Qwen 3.8 Markdown OCR Profile

**Input**: Design documents from `/specs/038-qwen38-markdown-prompts/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/qwen38-ocr-profile.md, quickstart.md

**Tests**: Tests are required by the specification and plan. Follow TDD within each story: add the focused unit and integration tests, confirm the missing behavior fails, then implement it.

**Organization**: Tasks are grouped by user story so each behavior can be implemented and validated incrementally while preserving standard, GLM, and FireRed request contracts.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it changes a different file and has no dependency on another incomplete task in the same phase
- **[Story]**: Maps the task to User Story 1, 2, or 3
- Every task names the exact repository file or focused test paths it affects

## Path Conventions

- Source code: `archivatorium/`
- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- Dependency metadata: `pyproject.toml`
- Feature design and validation: `specs/038-qwen38-markdown-prompts/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the current OCR request, cleanup, CLI, and timing baseline before Feature 038 changes.

- [X] T001 Run the focused baseline with `.venv/bin/python -m pytest -q tests/unit/test_ocr_engine.py tests/integration/test_ocr_cli.py` and record the passing count in `specs/038-qwen38-markdown-prompts/tasks.md` — baseline: 79 passed, 1 unrelated PyPDF2 deprecation warning

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Guarantee named reasoning-level support in every fresh project environment before the new profile is implemented.

**⚠️ CRITICAL**: No user story implementation begins until the dependency contract is established.

- [X] T002 Require the locally verified Ollama client version `ollama>=0.6.1` in `pyproject.toml` and verify project metadata still installs and type-checks — verified installed Ollama 0.6.1, editable-install metadata dry-run, and focused MyPy

**Checkpoint**: The dependency contract supports the precise `low`/`medium`/`high` reasoning levels required later by User Story 3.

---

## Phase 3: User Story 1 - Receive Markdown-native OCR output (Priority: P1) 🎯 MVP

**Goal**: Add an explicitly selectable `qwen38` mode whose dedicated prompts require pure Markdown, correct ATX heading hierarchy, column-one top-level blocks, Markdown tables, source fidelity, and artificial character de-spacing anywhere in text.

**Independent Test**: Select `--mode qwen38` with a custom Qwen 3.8 model identifier and inspect the outgoing mocked request. The new mode is accepted, uses its dedicated prompts, contains `#`/`##`/`###` hierarchy rules and the exact `N A T O   S E C R E T` → `NATO SECRET` generic de-spacing example, and preserves the selected model. Exact standard, GLM, and FireRed requests remain unchanged.

### Tests for User Story 1

> **NOTE: Complete T003-T004 first and confirm they fail because `qwen38` and its prompts do not exist.**

- [X] T003 [P] [US1] Add unit contract tests for Qwen 3.8 prompt constants, `qwen38` profile resolution, ATX heading rules, generic heading/prose/label/table-cell de-spacing, Markdown-only structure, table fallback, and unchanged existing profiles in `tests/unit/test_ocr_engine.py`
- [X] T004 [P] [US1] Add CLI integration tests proving `--mode qwen38` is accepted, preserves the exact `--model` value, uses the dedicated system/user messages and previous-page behavior, and leaves standard/GLM/FireRed requests unchanged in `tests/integration/test_ocr_cli.py`

### Implementation for User Story 1

- [X] T005 [US1] Add dedicated Qwen 3.8 prompt constants and an initial `QWEN38_OCR_PROFILE`, resolve `qwen38` without changing existing profiles in `archivatorium/ocr_engine.py`, and add `qwen38` to the existing mode choice in `archivatorium/cli.py`; implement the Markdown, heading, table, alignment, fidelity, context-safety, and generic de-spacing rules while reserving the prose-line and high-reasoning additions for later stories
- [X] T006 [US1] Run `tests/unit/test_ocr_engine.py` and `tests/integration/test_ocr_cli.py`, confirm User Story 1 and exact existing-mode isolation pass, and record the checkpoint result in `specs/038-qwen38-markdown-prompts/tasks.md` — checkpoint: 82 passed, 1 unrelated PyPDF2 deprecation warning

**Checkpoint**: The new mode is a usable Markdown-native OCR MVP with correct heading markers and generic artificial-spacing normalization; all existing modes are unchanged.

---

## Phase 4: User Story 2 - Preserve paragraphs as single lines (Priority: P2)

**Goal**: Make the Qwen 3.8 prompt require each prose paragraph on one physical line while preserving true paragraph and non-prose Markdown block boundaries.

**Independent Test**: Inspect the final Qwen 3.8 prompt request and mocked saved output for wrapped prose, separate paragraphs, headings, list items, pipe-table rows, and fenced content. The prompt explicitly joins only visual prose wraps, requires exactly one blank line between distinct paragraphs, and protects all other Markdown block boundaries.

### Tests for User Story 2

> **NOTE: Complete T007-T008 first and confirm the initial User Story 1 prompt lacks the complete paragraph contract.**

- [X] T007 [P] [US2] Add exact unit assertions for one-line prose, one blank line between distinct paragraphs, preserved headings/list items/table rows/fenced lines, and the complete final Qwen 3.8 system and user prompt text from `contracts/qwen38-ocr-profile.md` in `tests/unit/test_ocr_engine.py`
- [X] T008 [P] [US2] Add a Qwen 3.8 CLI integration test that captures the paragraph contract in the outgoing request and proves mocked compliant Markdown is saved without collapsing distinct blocks in `tests/integration/test_ocr_cli.py`

### Implementation for User Story 2

- [X] T009 [US2] Complete the Qwen 3.8 prompt constants with the single-line prose and blank-line separation rules, preserving the exact ordered contract and all User Story 1 rules in `archivatorium/ocr_engine.py`
- [X] T010 [US2] Run `tests/unit/test_ocr_engine.py` and `tests/integration/test_ocr_cli.py`, confirm the final prompt matches `specs/038-qwen38-markdown-prompts/contracts/qwen38-ocr-profile.md`, and record the checkpoint result in `specs/038-qwen38-markdown-prompts/tasks.md` — checkpoint: 84 passed, 1 unrelated PyPDF2 deprecation warning

**Checkpoint**: Qwen 3.8 mode has the complete final Markdown prompt contract, including safe single-line paragraphs.

---

## Phase 5: User Story 3 - Use high reasoning without leaking reasoning text (Priority: P3)

**Goal**: Send `think="high"` only for Qwen 3.8 mode while retaining reasoning cleanup and every existing mode's request shape.

**Independent Test**: Inspect first-attempt and retry requests plus saved Markdown. Qwen 3.8 requests use the selected model, identical messages/options, and `think="high"`; separate or inline reasoning is absent from saved content and subsequent-page context; standard and FireRed omit `think`, while GLM remains `false`.

### Tests for User Story 3

> **NOTE: Complete T011-T012 first and confirm Qwen 3.8 requests do not yet carry high reasoning.**

- [X] T011 [P] [US3] Add unit tests for the precise named reasoning type, Qwen 3.8 `think="high"`, identical retry requests, separate response reasoning isolation, inline final-`</think>` cleanup, clean previous-page context, and unchanged standard/GLM/FireRed reasoning fields in `tests/unit/test_ocr_engine.py`
- [X] T012 [P] [US3] Add CLI integration tests proving Qwen 3.8 sends `think="high"`, leaked reasoning is absent from saved Markdown, and standard still omits the reasoning field in `tests/integration/test_ocr_cli.py`

### Implementation for User Story 3

- [X] T013 [US3] Introduce a precise `bool | Literal["low", "medium", "high"] | None` profile reasoning type, set only `QWEN38_OCR_PROFILE` to `"high"`, and preserve existing response extraction and normalization in `archivatorium/ocr_engine.py`
- [X] T014 [US3] Run `tests/unit/test_ocr_engine.py` and `tests/integration/test_ocr_cli.py`, confirm reasoning isolation and all four mode contracts pass, and record the checkpoint result in `specs/038-qwen38-markdown-prompts/tasks.md` — checkpoint: 89 passed, 1 unrelated PyPDF2 deprecation warning

**Checkpoint**: All three stories are complete and independently observable through the new mode without regressions to existing OCR modes.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the complete request contract, documented examples, dependency metadata, and constitutional quality gates.

- [X] T015 Run the automated and prompt-inspection scenarios in `specs/038-qwen38-markdown-prompts/quickstart.md`, including `--help`, mode isolation, ATX headings, generic de-spacing, paragraph boundaries, tables, and reasoning cleanup, without committing live documents or model output — passed CLI help, exact prompt/mode inspection, and 30 targeted automated scenarios; no live data or model output used
- [X] T016 Run Ruff lint/format, Flake8, MyPy, the full pytest suite, and explicit coverage reporting using `pyproject.toml`, then record results and any unrelated pre-existing findings in `specs/038-qwen38-markdown-prompts/tasks.md` — Ruff and MyPy passed; Feature 038 Flake8 scope passed; full pytest passed 331 tests with one PyPDF2 warning; explicit coverage reported 95% overall (90% production coverage under pytest-cov); repository-wide Flake8 found the unrelated pre-existing `interlinking_service.py:358` complexity of 108 over 100, scheduled separately at user request

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Starts immediately and establishes the regression baseline.
- **Foundational (Phase 2)**: Depends on T001 and blocks story work until the Ollama reasoning-level dependency is reproducible.
- **User Story 1 (Phase 3)**: Depends on T002 and creates the new mode/profile used by later stories.
- **User Story 2 (Phase 4)**: Depends on the Qwen 3.8 prompt/profile from T005; its prompt edit must be serialized with T005 and T013.
- **User Story 3 (Phase 5)**: Depends on the Qwen 3.8 profile from T005 but is behaviorally independent of User Story 2; its production edit must be serialized with T009.
- **Polish (Phase 6)**: Depends on all selected stories.

### User Story Dependencies

- **User Story 1 (P1)**: Starts after the foundation and is the recommended MVP.
- **User Story 2 (P2)**: Requires the new mode to exist, then independently validates paragraph shaping through the prompt contract.
- **User Story 3 (P3)**: Requires the new profile to exist, then independently adds high reasoning and verifies reasoning isolation; it does not require User Story 2 behavior.

### Within Each User Story

- Write unit and integration tests first and confirm failure for the missing behavior.
- Unit and integration test tasks marked `[P]` may proceed together because they edit different files.
- Complete the single production task only after its story tests fail as expected.
- Run the focused checkpoint and commit a stable logical increment before the next production edit.
- Never combine unrelated local test edits, Spec Kit metadata, scripts, or datasets with Feature 038 commits.

### Parallel Opportunities

- T003 and T004 can run in parallel after T002.
- T007 and T008 can run in parallel after User Story 1.
- T011 and T012 can run in parallel after the Qwen 3.8 profile exists.
- User Stories 2 and 3 can prepare tests in parallel, but T009 and T013 both modify `archivatorium/ocr_engine.py` and must be serialized.
- T015 documentation validation and preparatory quality checks for T016 can overlap after all stories complete.

---

## Parallel Examples

### User Story 1

```text
Task T003: Add Qwen 3.8 prompt/profile unit contracts in tests/unit/test_ocr_engine.py
Task T004: Add qwen38 CLI integration contracts in tests/integration/test_ocr_cli.py
```

### User Story 2

```text
Task T007: Add final paragraph/prompt unit contracts in tests/unit/test_ocr_engine.py
Task T008: Add paragraph-contract CLI integration coverage in tests/integration/test_ocr_cli.py
```

### User Story 3

```text
Task T011: Add high-reasoning and cleanup unit contracts in tests/unit/test_ocr_engine.py
Task T012: Add visible qwen38 reasoning integration coverage in tests/integration/test_ocr_cli.py
```

---

## Implementation Strategy

### MVP First

1. Complete T001-T002 for baseline and dependency support.
2. Complete T003-T005 with tests first.
3. Run T006 and verify the new mode's Markdown, heading, table, alignment, fidelity, and generic de-spacing contract.
4. Stop at the User Story 1 checkpoint for a reviewable MVP while existing modes remain unchanged.

### Incremental Delivery

1. **Foundation**: Baseline plus verified named-reasoning dependency.
2. **US1 MVP**: New Qwen 3.8 mode with Markdown hierarchy and generic artificial-spacing rules.
3. **US2**: Complete the prompt with safe single-line prose paragraphs.
4. **US3**: Add high reasoning and verify cleanup/isolation.
5. **Polish**: Validate the exact contract, CLI, regressions, and quality gates.

### Parallel Team Strategy

1. Complete T001-T002 sequentially.
2. Within each story, prepare its unit and integration tests in parallel.
3. Serialize T005, T009, and T013 because they edit the shared OCR profile module.
4. Run T015-T016 after all story checkpoints pass.

---

## Notes

- `[P]` marks only tasks that touch separate files with no incomplete dependency.
- `[US1]`, `[US2]`, and `[US3]` provide direct traceability to the specification.
- Qwen 3.8 mode and model selection remain independent; no default model change is planned.
- Standard, GLM, and FireRed exact prompts and reasoning fields are immutable regression contracts for this feature.
- ATX headings, generic character de-spacing, pure Markdown, and single-line prose are prompt requirements; no heuristic output rewriter is introduced.
- Representative live inputs and outputs remain outside version control.
- Commit each completed task or cohesive test/implementation increment without staging unrelated files.
