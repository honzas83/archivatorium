# Implementation Plan: Resume-Safe Metadata and Prompt Isolation

**Branch**: `024-resume-safe-metadata` | **Date**: 2026-06-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/024-resume-safe-metadata/spec.md`

## Summary

The primary goal of this feature is to ensure that metadata processing in `ocrpolish` is resume-safe, prompt-isolated from previously generated outputs, and that citekeys are generated deterministically code-side. We will:
1. Implement a single preflight scan of the output folder at start to build tag, entity, and topic counters.
2. Ensure skipped files only contribute to counters if not already in the preflight scan to prevent double counting.
3. Strip all generated frontmatter, Metadata callouts, Abstract callouts, and citation callouts from content before passing to LLM prompts.
4. Exclude mentioned states, organizations, cities, and tags from the metadata LLM schema (handing tag/entity extraction completely to the tagging service).
5. Generate normalized deterministic BibTeX citekeys from output filename stems (or optionally, full vault paths).
6. Implement a clear, per-field reconciliation rule to preserve manual user metadata changes in existing frontmatter.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: click, ollama, pydantic, pyyaml, python-docx

**Storage**: files (input/output directories)

**Testing**: pytest

**Target Platform**: macOS, Linux

**Project Type**: cli

**Performance Goals**: Scan and skip 100+ already-processed files in under 5 seconds (excluding LLM calls).

**Constraints**: Complete prompt isolation (no generated sections fed back to LLM context).

**Scale/Scope**: 100-1000 Markdown files.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Quality-Driven Python Development**: Passed. We use Python 3.12 with `ruff`, `mypy`, and `pytest`.
- **CLI-First Interface**: Passed. The new citekey mode option is integrated directly into the `ocrpolish metadata` click command.
- **Recursive Directory Processing**: Passed. Both preflight scan and processing recursive traversal remain fully functional.
- **Data Isolation**: Passed. All test inputs/outputs are placed in local dirs and gitignored.
- **Atomic Git Workflow**: Passed. Work tasks will be committed sequentially.

## Project Structure

### Documentation (this feature)

```text
specs/024-resume-safe-metadata/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── cli.md           # CLI interface contract
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
ocrpolish/
├── models/
│   └── metadata.py      # MetadataSchema and CanonicalTags updates
├── utils/
│   └── metadata.py      # Stripping logic, reconciliation logic, citekey generation
├── cli.py               # Add --citekey-mode option
└── processor_metadata.py # Preflight scan once flag, skip loop integration

tests/
├── unit/
│   ├── test_metadata_stripping.py
│   ├── test_citekey_generation.py
│   └── test_reconciliation.py
└── integration/
    └── test_resume_safety.py
```

**Structure Decision**: Single project layout.

## Complexity Tracking

*No violations of project constitution principles. No complexity override needed.*
