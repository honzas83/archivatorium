# Tasks: Obsidian Markdown Metadata

**Input**: Design documents from `specs/009-obsidian-markdown-metadata/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Update `ocrpolish/data_model.py` to include `vault_root` and `pdf_dir` in `ProcessingConfig`
- [x] T002 Update `ocrpolish/cli.py` to add `--vault-root` and `--pdf-dir` options to the `metadata` command
- [x] T003 Update `ocrpolish/processor_metadata.py` `MetadataProcessor.__init__` to accept `vault_root` and `pdf_dir`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Implement recursive dictionary flattening with underscores in `ocrpolish/utils/metadata.py`
- [x] T005 [P] Implement tag normalization (removing '#' and spaces) in `ocrpolish/utils/metadata.py`
- [x] T006 [P] Add unit tests for flattening and tag normalization in `tests/unit/test_metadata_utils.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Obsidian Native Metadata (Priority: P1) 🎯 MVP

**Goal**: Output metadata in a flattened YAML frontmatter within a Markdown file.

**Independent Test**: Process a Markdown file and verify the output has a valid, non-nested YAML frontmatter at the top.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

- [x] T007 [P] [US1] Create integration test in `tests/integration/test_obsidian_metadata.py` for flattened frontmatter output

### Implementation for User Story 1

- [x] T008 [US1] Update `ocrpolish/processor_metadata.py` to use the flattening logic when preparing `metadata_dict`
- [x] T009 [US1] Update `ocrpolish/utils/metadata.py` `prepend_frontmatter` to ensure it always uses the Markdown format (standardizing the opening/closing `---`)
- [x] T010 [US1] Update `MetadataProcessor.process_file` in `ocrpolish/processor_metadata.py` to write the output as a `.md` file regardless of original extension (though usually already .md)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Source Document Linking (Priority: P2)

**Goal**: Include an Obsidian internal link `[[path/to/filename.pdf]]` in the frontmatter.

**Independent Test**: Verify the `source` property in the frontmatter contains the correct relative path to the PDF.

### Tests for User Story 2

- [x] T011 [P] [US2] Add test case to `tests/integration/test_obsidian_metadata.py` for source PDF relative path calculation

### Implementation for User Story 2

- [x] T012 [US2] Implement relative path calculation logic from vault root in `ocrpolish/utils/files.py` or `ocrpolish/utils/metadata.py`
- [x] T013 [US2] Update `MetadataProcessor.process_file` in `ocrpolish/processor_metadata.py` to calculate the PDF path and add it to `metadata_dict["source"]`
- [x] T014 [US2] Ensure the PDF filename is derived from the input Markdown filename (replacing `.md` with `.pdf`)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Obsidian Tag Integration (Priority: P3)

**Goal**: keywords/hashtags formatted as plain strings in the `tags` YAML property.

**Independent Test**: Verify the `tags` list in the frontmatter contains no `#` prefixes.

### Tests for User Story 3

- [x] T015 [P] [US3] Add test case to `tests/integration/test_obsidian_metadata.py` to verify tag cleaning in output

### Implementation for User Story 3

- [x] T016 [US3] Update `MetadataProcessor.process_file` in `ocrpolish/processor_metadata.py` to clean tags before adding to `metadata_dict`
- [x] T017 [US3] Ensure tags are passed as a list to `yaml.safe_dump` for correct list formatting in frontmatter

### User Story 4 - Abstract Callout (Priority: P4)

**Goal**: Present the abstract as a highly visible Obsidian Callout.

**Independent Test**: Verify the document body starts with a `> [!abstract]` block containing the abstract text.

- [x] T023 [US4] Implement `format_as_callout` in `ocrpolish/utils/metadata.py`
- [x] T024 [US4] Update `MetadataProcessor.process_file` to insert the abstract callout into the document body
- [x] T025 [P] [US4] Add test case to `tests/integration/test_obsidian_metadata.py` for abstract callout presence

**Checkpoint**: All user stories should now be independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T018 [P] Update `specs/009-obsidian-markdown-metadata/quickstart.md` with any actual CLI parameter names if changed during implementation
- [x] T019 Run `ruff check .` and `ruff format .`
- [x] T020 Run `mypy .`
- [x] T021 Run `pytest` and ensure all tests pass with coverage
- [x] T022 [P] Perform manual validation with an actual Obsidian vault sample in `data/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories proceed in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### Parallel Opportunities

- T005, T006 can run in parallel within Phase 2.
- T007, T011, T015 can be set up in parallel.
- Polish tasks T018-T022 can run in parallel where independent.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & 2 (Setup + Foundational).
2. Complete Phase 3 (User Story 1 - Flattening & MD output).
3. Validate that basic Obsidian metadata is generated.

### Incremental Delivery

1. Add User Story 2 (Linking) and test.
2. Add User Story 3 (Tags) and test.
3. Final polish and verification.
