# CLI Contract: Obsidian Vault Interlinking

## Command: `interlink`

Post-processes a generated Obsidian vault in-place to interlink documents based on `archive_code`.

### Usage
```bash
ocrpolish interlink [OPTIONS] VAULT_DIR
```

### Arguments
- `VAULT_DIR`: Path to the root of the Obsidian vault to process.

### Options
- `--dry-run`: Log planned changes without modifying files.
- `--verbose`: Show detailed mapping and matching logs.

### Behavioral Rules
1. **First Pass (Discovery)**:
    - Recursively scan `VAULT_DIR` for `*.md` files.
    - Extract `archive_code` and `language` from YAML frontmatter.
    - Normalize `archive_code` (remove whitespace).
    - Store mapping: `normalized_code -> language -> relative_path`.

2. **Second Pass (Processing)**:
    - For each file:
        - **Metadata Callout**:
            - Find `[!info] Metadata` callout.
            - Resolve `references` using language priority: Current -> English -> Any.
            - Convert references to `[Code](Path)`.
            - Insert `language_versions` row if other versions exist.
        - **Body**:
            - Find all occurrences of known `archive_code`s.
            - Match on prefix-boundary.
            - Prioritize longest match.
            - Convert to `[Code](Path)`.
        - **Persistence**: Write back to file.

### Exit Codes
- `0`: Success.
- `1`: Invalid `VAULT_DIR` or general error.
