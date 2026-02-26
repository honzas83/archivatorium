# Tasks: Improve DOCX Header and Footer Export

**Feature Name**: Improve DOCX Header and Footer Export
**Plan**: [plan.md](./plan.md)

## Phase 1: Setup

- [X] T001 Initialize feature test data in `data/test/007-docx-enhancement`
- [X] T002 [P] Create unit test for page metadata extraction in `tests/unit/test_docx_metadata.py`
- [X] T003 [P] Create integration test for basic DOCX sectioning in `tests/integration/test_docx_generation.py`

## Phase 2: Foundational

- [X] T004 Define `PageMetadata` data class in `ocrpolish/data_model.py`
- [X] T005 Implement sliding-window logic for nearness detection in `ocrpolish/core.py`
- [X] T006 Add section-styling helpers in `ocrpolish/utils/docx_utils.py`

## Phase 3: User Story 1 - Automated "PDF Page N" Footer (Priority: P1)

**Goal**: Ensure every page has a right-aligned "PDF Page N" footer.
**Independent Test**: Verify DOCX output for multiple `# Page N` markers contains matching footers on each page.

- [X] T007 [US1] Update `DocxProcessor` to split document into sections based on `# Page N` markers in `ocrpolish/processor.py`
- [X] T008 [US1] Implement "PDF Page N" footer injection for each section in `ocrpolish/processor.py`
- [X] T009 [US1] Handle blank page generation for consecutive `# Page N` markers in `ocrpolish/processor.py`

## Phase 4: User Story 2 - Metadata Isolation (Priority: P1)

**Goal**: Isolate original page numbers (`-X-`) and prevent inheritance.
**Independent Test**: Verify a page without `-X-` marker has empty headers/footers (except PDF Page N).

- [X] T010 [US2] Implement original page number (`-X-`) extraction from page text in `ocrpolish/core.py`
- [X] T011 [US2] Update `DocxProcessor` to clear header/footer text if no `-X-` is found on current page in `ocrpolish/processor.py`

## Phase 5: User Story 3 - Contextual Metadata Migration (Priority: P2)

**Goal**: Move filtered lines near markers to headers/footers.
**Independent Test**: Verify filtered lines near `-X-` markers are moved to correct margins and aligned properly.

- [X] T012 [US3] Implement logic to identify filtered lines near first/last `-X-` markers in `ocrpolish/core.py`
- [X] T013 [US3] Implement four-way alignment logic for metadata in headers/footers in `ocrpolish/processor.py`
- [X] T014 [US3] Implement metadata joining with " | " separator in `ocrpolish/processor.py`

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T015 Verify sidecar `.filtered.md` files are unaffected by metadata migration in `tests/integration/test_sidecar_output.py`
- [X] T016 Run `ruff check .` and `mypy .` to ensure code quality
- [X] T017 Final end-to-end validation with various marker combinations

## Dependencies

- Phase 2 must be complete before Phase 3.
- US1 (Phase 3) is a prerequisite for US2 and US3 as it establishes the section-based structure.
- US2 and US3 can be developed partially in parallel once US1 foundations are in place.

## Parallel Execution Examples

- **Metadata Extraction**: T002 and T003 can be written in parallel.
- **Foundational Logic**: T005 and T006 can be implemented in parallel.
- **US2 & US3**: T010 and T012 involve different parts of the extraction logic and can be started together.

## Implementation Strategy

- **MVP**: Complete Phase 3 (US1) to establish the basic page numbering and sectioning. This provides immediate value.
- **Incremental**: Add metadata isolation (US2) and then the migration logic (US3) as separate, stable increments.
