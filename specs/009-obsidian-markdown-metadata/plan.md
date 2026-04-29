# Implementation Plan: Obsidian Markdown Metadata

**Branch**: `009-obsidian-markdown-metadata` | **Date**: 2026-04-29 | **Spec**: [specs/009-obsidian-markdown-metadata/spec.md](spec.md)
**Input**: Feature specification from `/specs/009-obsidian-markdown-metadata/spec.md`

## Summary

The goal of this feature is to change the format of the generated metadata from YAML (nested) to a Markdown file with a YAML frontmatter tailored for Obsidian. This includes flattening nested metadata structures using underscores, converting hashtags/keywords into Obsidian-compatible tags, adding an Obsidian-style link to the source PDF using its relative path from the vault root, and presenting the abstract as an Obsidian Callout at the start of the body.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: `click`, `PyYAML`, `pydantic` (already in project)
**Storage**: Filesystem (input/output directories)  
**Testing**: pytest, coverage  
**Target Platform**: CLI (cross-platform Python)
**Project Type**: Single project
**Performance Goals**: Processing a single file's metadata should be completed in < 100ms.
**Constraints**: Must maintain directory mirroring; output must be `.md`.
**Scale/Scope**: Operates on a single-file level, following established recursive patterns.
**Vault Relative Paths**: [NEEDS CLARIFICATION: How will the system determine the 'vault root' to calculate the relative path to the PDF?]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Principle I: Quality-Driven Python Development (Python 3.12, ruff, mypy, pytest)
- [x] Principle II: CLI-First Interface (Extending `click` CLI)
- [x] Principle III: Recursive Directory Processing (Reusing existing processor logic)
- [x] Principle IV: Data Isolation (Using `data/` for test samples)
- [x] Principle V: Atomic Git Workflow (Planned commits per task)

## Project Structure

### Documentation (this feature)

```text
specs/009-obsidian-markdown-metadata/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── checklists/
    └── requirements.md  # Specification Quality Checklist
```

### Source Code (repository root)

```text
ocrpolish/
├── cli.py               # Update CLI to support .md metadata output and new path options
├── core.py              # Update processor logic for Markdown generation and path calculation
├── data_model.py        # Update/Add Pydantic models for Obsidian metadata
└── utils/
    ├── metadata.py      # Logic for flattening, tag conversion, and path formatting
    └── files.py         # File naming and extension handling
```

**Structure Decision**: Single project structure as per Principle I and existing repository layout.

## Complexity Tracking

*No violations identified.*
