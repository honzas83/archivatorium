# Implementation Plan: Inverted Paragraph Merging & Wrapping

**Branch**: `002-wrap-long-paragraphs` | **Date**: 2026-02-12 | **Spec**: /specs/002-wrap-long-paragraphs/spec.md
**Input**: Feature specification from `/specs/002-wrap-long-paragraphs/spec.md`

## Summary

Implement a new line-wrapping strategy in `ocrpolish`. Instead of merging lines into paragraphs, the system will process each line independently. If a line exceeds the `typewriter_width`, it will be hard-wrapped using a word-wrap algorithm, with all wrapped lines being flush left.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: `textwrap` (Python Standard Library)
**Storage**: Filesystem (input/output mirroring)
**Testing**: pytest, coverage
**Target Platform**: CLI (cross-platform Python)
**Project Type**: Single project
**Performance Goals**: Fast per-line processing using efficient standard library wrapping.
**Constraints**: Recursive processing, directory mirroring, hard-wrap only (no merge).
**Scale/Scope**: Modify `processor.py` to change `merge_paragraphs` logic to `wrap_lines` logic.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Quality-Driven Python Development**: Uses Python 3.12 and established quality gates.
- [x] **II. CLI-First Interface**: Already uses `argparse` from feature 001.
- [x] **III. Recursive Directory Processing**: Existing utility in `utils/files.py` will be reused.
- [x] **IV. Data Isolation**: Continues to use `data/` for samples.
- [x] **V. Atomic Git Workflow**: Plan supports logical incremental commits.

## Project Structure

### Documentation (this feature)

```text
specs/002-wrap-long-paragraphs/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (already exists, no major changes)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
ocrpolish/
├── processor.py         # Primary logic changes (wrap instead of merge)
├── cli.py               # Verify --width handling
└── core.py              # Ensure Pass 2 calls updated logic correctly
```

**Structure Decision**: No change to existing structure.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A       |            |                                     |
