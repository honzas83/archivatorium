# Research: OCR Post-Processing

## Decisions

### Statistical Header/Footer Detection
- **Decision**: Use a global `Counter` to track line frequencies across all matching files in the first pass.
- **Rationale**: A frequency threshold of 50% allows identifying boilerplate text that appears in the majority of documents. A two-pass approach ensures we have global context before removing any content.
- **Alternatives Considered**: Local-only detection; Exact match across all files.

### Paragraph Merging Heuristics
- **Decision**: Merge lines if the current line does not start with a Markdown symbol (`-`, `*`, `#`, `|`, `>`) and the previous line does not indicate a paragraph break.
- **Rationale**: Protects standard Markdown structures as required by clarifications.
- **Alternatives Considered**: Pure regex-based line merging.

### CLI Framework
- **Decision**: Use `argparse`.
- **Rationale**: Standard library module, zero external dependencies, and specifically requested by the user for simplicity.
- **Alternatives Considered**: `click` (rejected as per user instruction).

### Directory Mirroring
- **Decision**: Use `pathlib` for all path manipulations.
- **Rationale**: Modern, object-oriented approach to filesystem paths in Python.
- **Alternatives Considered**: `os.path`.
