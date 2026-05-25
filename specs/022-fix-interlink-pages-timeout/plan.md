# Implementation Plan: fix-interlink-pages-timeout

**Branch**: `022-fix-interlink-pages-timeout` | **Date**: 2026-05-25 | **Spec**: [specs/022-fix-interlink-pages-timeout/spec.md](spec.md)

**Input**: Feature specification from `/specs/022-fix-interlink-pages-timeout/spec.md`

## Summary
Fixes archive code unification, page counting, and Ollama timeouts. The unification logic is now modular, reading regex-based rules from an external YAML file (`topics/unifications.yaml`) and applying them globally to all archive codes.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: `click`, `ollama`, `PyYAML`
**Testing**: `pytest`

## Constitution Check

- [x] Python (Principle I)
- [x] CLI-First (Principle II)
- [x] Modular Design (Clarified Requirement)

## Project Structure

### Documentation
```text
specs/022-fix-interlink-pages-timeout/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/cli.md
```
### Source Code
```text
ocrpolish/
├── cli.py                       # Add --unifications option to interlink
├── services/
│   ├── interlinking_service.py  # Load YAML rules from provided or default path
│   └── ollama_client.py         # 300s timeout
└── utils/
    └── metadata.py             # Header-based page counting
```

topics/
└── unifications.yaml           # New: configuration file
```

**Structure Decision**: Single project. Modular rule loading in `InterlinkingService`.
