# Tasks: Resume-Safe Metadata and Prompt Isolation

**Input**: Design documents from `/specs/024-resume-safe-metadata/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, or US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure validation

- [X] T001 Verify active python environment has all requirements installed
- [X] T002 [P] Verify code formatting and baseline styling configuration by running `ruff check .`
- [X] T003 [P] Verify baseline typing by running `mypy .`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core model updates required by all downstream metadata processor features

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Update the `MetadataSchema` Pydantic model in `ocrpolish/models/metadata.py` by removing obsolete fields (`mentioned_states`, `mentioned_organisations`, `mentioned_cities`, `tags`) and ensuring all other fields match the canonical list.

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Resume-Safe Processing with Preflight Scan (Priority: P1) 🎯 MVP

**Goal**: Implement a preflight scan of the output directory exactly once at startup, skipped files contribute to tag counters only if not already scanned, and prevent double-counting.

**Independent Test**: Run metadata pipeline on a folder, cancel, run again with `--overwrite false`; verify skipped files do not duplicate tags in counters.

### Tests for User Story 1

- [X] T005 [P] [US1] Create integration tests for resume-safe scanning and counter population in `tests/integration/test_resume_safety.py`.

### Implementation for User Story 1

- [X] T006 [US1] Add a boolean `_preflight_done` flag and update `preflight_scan` to run exactly once per lifecycle in `ocrpolish/processor_metadata.py`.
- [X] T007 [US1] Update `process_file` in `ocrpolish/processor_metadata.py` to parse skipped files and add their tags to counters only if they were not already loaded during the preflight scan.
- [X] T008 [US1] Ensure `process_directory` triggers `preflight_scan` at startup in `ocrpolish/processor_metadata.py`.

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Clean Markdown Content Extraction and Prompt Isolation (Priority: P1)

**Goal**: Clean input Markdown files before building LLM prompts by stripping previously generated frontmatter and callout sections (Metadata, Abstract, Citation).

**Independent Test**: Reprocess an already enriched file; verify that context sent to the LLM does not contain any generated frontmatter or callouts.

### Tests for User Story 2

- [X] T009 [P] [US2] Create unit tests verifying stripping regexes on various enriched Markdown structures in `tests/unit/test_metadata_stripping.py`.

### Implementation for User Story 2

- [X] T010 [US2] Implement the `strip_generated_sections(content: str) -> str` utility function in `ocrpolish/utils/metadata.py` using regular expressions.
- [X] T011 [US2] Integrate `strip_generated_sections` into `process_file` in `ocrpolish/processor_metadata.py` before passing text content to prompt templates.

**Checkpoint**: User Story 2 is fully functional and prevents LLM feedback loops.

---

## Phase 5: User Story 3 - Clean and Reconciled Metadata Schema (Priority: P2)

**Goal**: Render only canonical fields in frontmatter/table, calculate deterministic BibTeX citekey code-side, handle custom navigation labels, and reconcile existing frontmatter.

**Independent Test**: Verify that citekey matches normalized stem/path, that obsolete fields are removed, and manually edited frontmatter fields are preserved.

### Tests for User Story 3

- [X] T012 [P] [US3] Create unit tests for deterministic citekey generation (stem and path modes) in `tests/unit/test_citekey_generation.py`.
- [X] T013 [P] [US3] Create unit tests for deterministic per-field reconciliation rules in `tests/unit/test_reconciliation.py`.

### Implementation for User Story 3

- [X] T014 [US3] Implement citekey generation and safe character normalization logic (`generate_citekey`) in `ocrpolish/utils/metadata.py`.
- [X] T015 [US3] Update the CLI click entry point in `ocrpolish/cli.py` to add the `--citekey-mode [stem|path]` command line option.
- [X] T016 [US3] Implement metadata reconciliation logic (`reconcile_metadata`) according to the per-field rules in `ocrpolish/utils/metadata.py`.
- [X] T017 [US3] Update `_prepare_obsidian_metadata` and output generation in `ocrpolish/processor_metadata.py` to use reconciled metadata, format citekeys, exclude `abstract` from frontmatter/table, and render it in the body Abstract callout.
- [X] T018 [US3] Update the Metadata table formatting in `ocrpolish/utils/metadata.py` to support derived navigation fields labeled with `(derived)`.

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Cleanup, formatting, quality assurance, and quickstart validation

- [X] T019 [P] Verify code quality and styling compliance by running `ruff check .` and `ruff format .`
- [X] T020 [P] Run static typing checks using `mypy .`
- [X] T021 Run all test suites and verify coverage via `coverage run -m pytest`
- [X] T022 Execute quickstart validation scenarios from `specs/024-resume-safe-metadata/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion. Blocks all User Stories.
- **User Stories (Phases 3-5)**: Depend on Foundational completion.
  - US1 (Phase 3) and US2 (Phase 4) can proceed in parallel once Phase 2 is complete.
  - US3 (Phase 5) should start after US1 and US2 are completed as it handles reconciliation of stripped structures and updates formatting.
- **Polish (Phase 6)**: Depends on all user story phases.

### Parallel Opportunities

- All Setup tasks (`T001`-`T003`) can run in parallel.
- Test creation tasks `T005`, `T009`, `T012`, and `T013` can be created in parallel.
- Polish tasks `T019` and `T020` can run in parallel.

---

## Parallel Example: User Story 3

```bash
# Launch test creation tasks for User Story 3 in parallel:
Task: "Create unit tests for deterministic citekey generation in tests/unit/test_citekey_generation.py"
Task: "Create unit tests for deterministic per-field reconciliation rules in tests/unit/test_reconciliation.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (Update Pydantic model)
3. Complete Phase 3: User Story 1 (Resume-Safety)
4. Complete Phase 4: User Story 2 (Prompt Isolation)
5. **STOP and VALIDATE**: Verify skipped file counters and prompt text isolation.

### Incremental Delivery
1. Add User Story 3 (Metadata Schema & Reconciliation).
2. Validate using `quickstart.md`.
3. Complete Phase 6: Polish (ruff, mypy, test coverage).
