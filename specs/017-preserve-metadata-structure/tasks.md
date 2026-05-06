# Tasks: Preserve Metadata Directory Structure

**Input**: Design documents from `specs/017-preserve-metadata-structure/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

## Phase 1: Setup (Shared Infrastructure)

- [x] T001 [P] Create `mirror_file` and `safe_read_text` helper skeletons in `ocrpolish/utils/metadata.py`
- [x] T002 [P] Update `MetadataProcessor` constructor to ensure all necessary path variables are initialized in `ocrpolish/processor_metadata.py`

## Phase 2: Foundational (Blocking Prerequisites)

- [x] T003 Update `MetadataProcessor.get_files` to support identifying all file types for mirroring in `ocrpolish/processor_metadata.py`
- [x] T004 Implement directory structure replication logic in `MetadataProcessor.process_directory` in `ocrpolish/processor_metadata.py`

## Phase 3: User Story 1 - Mirror Directory Structure (Priority: P1) 🎯 MVP

**Goal**: Replicate the source directory hierarchy in the output folder.

**Independent Test**: Run the metadata command on a nested source directory and verify the output has the same folder tree.

### Implementation for User Story 1

- [x] T005 [US1] Update `process_directory` to calculate `relative_path` for all items in `ocrpolish/processor_metadata.py`
- [x] T006 [US1] Implement automatic creation of parent directories in `MetadataProcessor.process_file` and `process_directory` using `path.parent.mkdir(parents=True, exist_ok=True)` in `ocrpolish/processor_metadata.py`
- [x] T007 [US1] Ensure the `output_file` path preserves the original filename and extension during directory traversal in `ocrpolish/processor_metadata.py`

---

## Phase 4: User Story 3 - Enriched Markdown Files (Priority: P1)

**Goal**: Process Markdown files with robust UTF-8 handling and enrichment.

**Independent Test**: Verify that an MD file with invalid UTF-8 bytes is processed without crashing and the output is valid UTF-8.

### Implementation for User Story 3

- [x] T008 [US3] Implement `safe_read_text` with `errors='replace'` in `ocrpolish/utils/metadata.py`
- [x] T009 [US3] Update `MetadataProcessor.process_file` to use `safe_read_text` for reading source markdown in `ocrpolish/processor_metadata.py`
- [x] T010 [US3] Ensure `output_file.write_text` explicitly uses `encoding='utf-8'` in `ocrpolish/processor_metadata.py`
- [x] T011 [P] [US3] Add unit tests for `safe_read_text` with malformed input in `tests/unit/test_metadata_utils.py`

---

## Phase 5: User Story 2 - Efficient File Mirroring (Priority: P2)

**Goal**: Use hardlinks for non-markdown files to save space and time.

**Independent Test**: Verify that a PDF in the output directory has the same inode as the source PDF.

### Implementation for User Story 2

- [x] T012 [US2] Implement `os.link` logic with `shutil.copy2` fallback in `ocrpolish/utils/metadata.py`
- [x] T013 [US2] Update `MetadataProcessor.process_directory` to call `mirror_file` for all non-markdown files in `ocrpolish/processor_metadata.py`
- [x] T014 [P] [US2] Add integration test to verify hardlink creation on supporting filesystems in `tests/integration/test_mirroring.py`
- [x] T018 [US4] Implement PDF placement in `pdf/` subdirectories and update `_get_pdf_link` logic
- [x] T019 [P] [US4] Add integration test for `pdf/` subdirectory and link verification in `tests/integration/test_pdf_subdirectory.py`

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T015 [P] Update `ocrpolish/cli.py` to ensure `metadata` command correctly passes the `recursive` flag to the processor
- [x] T016 [P] Documentation update: Ensure `README.md` or `quickstart.md` reflects the mirroring behavior
- [x] T017 [P] Final quality check: Run `ruff check .`, `mypy .`, and `pytest`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Initial helpers.
- **Foundational (Phase 2)**: Core traversal logic.
- **User Stories (Phase 3 & 4)**: Can proceed in parallel once Phase 2 is done. Both are P1.
- **User Story 2 (Phase 5)**: Can proceed after Phase 2, but depends on `mirror_file` helper from Phase 1.
- **Polish (Phase 6)**: Final verification.

---

## Implementation Strategy

1. **Foundational First**: Get the directory traversal working so files are placed in the right spots.
2. **P1 Stories**: Focus on Markdown enrichment and UTF-8 safety.
3. **P2 Optimization**: Add hardlinking as a performance enhancement once mirroring is stable.
