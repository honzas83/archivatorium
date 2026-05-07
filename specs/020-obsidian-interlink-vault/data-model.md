# Data Model: Obsidian Vault Interlinking

## Entities

### VaultDocument
Represents a Markdown file within the Obsidian vault.
- **path**: `Path` - Absolute path to the file.
- **vault_relative_path**: `str` - Path relative to the vault root (used for links).
- **archive_code**: `str` - The raw archive code from frontmatter.
- **normalized_code**: `str` - Archive code with all whitespace removed.
- **language**: `str` - The document language from frontmatter.
- **references**: `list[str]` - List of archive codes referenced by this document.

### ArchiveCodeMap
A global lookup table built during the first pass.
- **mapping**: `dict[str, dict[str, str]]`
    - Key (Outer): `normalized_code`
    - Key (Inner): `language`
    - Value: `vault_relative_path`

## State Transitions
1. **Discovery**: Scan the vault, parse frontmatter of all `*.md` files, and populate `ArchiveCodeMap`.
2. **Interlinking**: Iterate through all files again:
    - Update "Metadata" callout table rows (`references`, `language_versions`).
    - Search body text for `normalized_code` patterns and convert to Markdown links.
    - Write modified content back to the same file.
