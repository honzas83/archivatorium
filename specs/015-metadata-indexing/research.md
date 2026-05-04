# Research: Metadata Indexing

## Decision: XLSX Library
**Decision**: Use `XlsxWriter`.
**Rationale**: It is a lightweight, feature-rich library for creating Excel files. It doesn't require Excel to be installed and provides excellent control over cell formatting, which is useful for headers.
**Alternatives considered**: 
- `pandas`: Overkill for simple row-based export.
- `openpyxl`: Good alternative, but `XlsxWriter` is generally faster for writing large files from scratch.

## Decision: Abstract Callout Parsing
**Decision**: Use regex to extract the `[!abstract]` callout block and then use regex again to find all hashtags within it.
**Rationale**: Callouts in Obsidian are block-level elements starting with `> [!abstract]`. A regex can reliably capture the block by matching consecutive lines starting with `>`. Inside the block, hierarchical tags follow the pattern `#[A-Za-z0-9/-]+`.
**Alternatives considered**: 
- `python-markdown` parser: More robust but adds a dependency and might be slower for just extracting one block.

## Decision: Entity Extraction & Merging
**Decision**: 
1. Extract flat tags from frontmatter `tags` field.
2. Extract hierarchical tags from the `[!abstract]` block.
3. Merge and deduplicate. 
4. Filter by predefined prefixes: `State`, `City`, `Org`, `Category`.
**Rationale**: This ensures we capture all relevant entities regardless of where they are stored.

## Decision: Topics Index Structure
**Decision**: Load `topics_yaml` (provided via CLI) to get descriptions and hierarchy. Only include topics found in the vault.
**Rationale**: The user wants the index to include descriptions from the YAML, making it more informative than just a list of tags.

## Decision: Implementation Path
**Decision**: Create a new service `ocrpolish/services/indexing_service.py` to handle the logic, and update `ocrpolish/cli.py` to add the `index` subcommand.
**Rationale**: Keeps the core logic separate from the CLI interface, following existing project patterns.
