# Research: Obsidian Vault Interlinking

## Decisions

### 1. Document Parsing & In-place Modification
- **Decision**: Use a line-by-line streaming approach or regex-based replacement for in-place modification.
- **Rationale**: Since we are modifying the "Metadata" callout table and the body, we need to be precise to avoid corrupting other Markdown elements.
- **Alternatives**: Using a full Markdown parser (like `mistune` or `markdownit`), but these often reconstruct the entire document, potentially losing original formatting or custom Obsidian syntax.

### 2. Archive Code Normalization & Matching
- **Decision**: Normalize archive codes by removing all whitespace: `normalized = re.sub(r"\s+", "", code)`.
- **Matching Logic**:
    - Use a regex that matches the archive code at a prefix boundary.
    - Boundary rule: The character immediately following the match in the target string must be non-alphanumeric (e.g., `(`, `/`, `-`, space) or the end of the string.
    - Priority: When multiple documents match as prefixes, the **longest match** is selected.
- **Rationale**: This prevents `DPC/D(69)5` from matching `DPC/D(69)58` while allowing `DPC/D(69)58` to match `DPC/D(69)58(Revised)`.

### 3. Language Fallback & Cross-linking
- **Decision**:
    - **Step 1**: Scan all files to build a mapping: `normalized_code -> {lang: full_vault_path}`.
    - **Step 2**: During processing:
        - For `references`: Look up `normalized_code`. Try current lang, then `English`, then any available.
        - For `language_versions`: Find all keys in the inner dict excluding the current language.
- **Rationale**: Efficiently handles the fallback requirements and enables cross-linking across the entire vault.

### 4. Metadata Callout Modification
- **Decision**: Target the `[!info] Metadata` callout block.
- **References**: Replace the value in the `| ☰&nbsp;references: | ... |` row.
- **Language Versions**: Insert a new row `| ≡&nbsp;language_versions: | ... |` immediately after the `language:` row.
- **Rationale**: Complies with the requirement to NOT modify YAML frontmatter.

### 5. Idempotency & Link Replacement
- **Decision**: Use regex that accounts for existing Markdown links when matching archive codes in the body and callout table.
- **Logic**:
    - Before wrapping an archive code in a link, check if it's already part of a Markdown link `[Title](Path)`.
    - If it is, replace the entire link structure with the new resolved link.
    - Specifically for the "Metadata" callout table, the replacement should be surgical within the cell content.
- **Rationale**: Prevents link nesting and ensures that if a document's path or language fallback changes, the vault can be updated by re-running the command.

## Technical Details

- **Regex for Metadata Callout**: `^> \[!info\] Metadata.*?(?=\n\n|\n[^>])` (multi-line, dotall).
- **Regex for Table Rows**: `\| (.*?references:) \| (.*?) \|` and `\| (.*?language:) \| (.*?) \|`.
- **Body Interlinking**: Scan the text for any known `archive_code`. Sort known codes by length descending to ensure longest match first.
