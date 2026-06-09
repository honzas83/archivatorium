# Data Model and Schema Specification

This document defines the structured records, file schemas, and models used in the unified interlinking and finalization workflow.

## 1. VaultDocument (In-Memory Record)

A structured representation of a markdown document scanned from the vault.

| Field Name | Type | Description |
|---|---|---|
| `path` | `pathlib.Path` | Absolute path on disk. |
| `vault_relative_path` | `str` | Path relative to the vault root (e.g., `NPG/NPG-D-74-2.md`). |
| `body` | `str` | Clean markdown body (excluding YAML frontmatter). |
| `frontmatter` | `dict[str, Any]` | Parsed YAML frontmatter key-value pairs. |
| `archive_code` | `str` | Normalized canonical archive code (e.g., `NPG/D(74)2`). |
| `language` | `str` | Primary document language (e.g., `English` or `French`). |
| `raw_references` | `list[str]` | References extracted from the frontmatter or metadata table. |
| `canonical_tags` | `CanonicalTags` | Parsed canonical tag collections (States, Cities, Orgs, People, Topics, Tags). |

## 2. Spreadsheet Export Schema (`metadata_index.xlsx`)

The pivoted spreadsheet export structure.

### Core Document Metadata Columns
1. `File Path`: Vault-relative path of the markdown file.
2. `Citekey`: Stable citation key derived from the filename/vault path.
3. `Title`: The document title (original language, natural casing).
4. `Summary`: One-sentence document summary.
5. `Date`: Document date in ISO 8601 format.
6. `Archive Code`: Original archive reference code.
7. `Language`: Primary language.
8. `Location City`: Origin city.
9. `Location State`: Origin state.
10. `Sender`: Sender name/institution.
11. `Recipient`: Recipient name/institution.
12. `Intent`: Intent of the correspondence.
13. `References`: Comma-separated list of resolved/unresolved archive references.
14. `Language Versions`: Comma-separated list of alternative language version links.

### Pivoted Tag Model Columns (Extracted using `CanonicalTagParser`)
1. `conceptual_tags`: Comma-separated list of flat concept tags (prefixed with `#Tags/`).
2. `topic_tags`: Comma-separated list of topic tags (prefixed with `#Topics/`).
3. `state_entities`: Comma-separated list of state entities (prefixed with `#Entities/State/`).
4. `org_entities`: Comma-separated list of organization entities (prefixed with `#Entities/Org/`).
5. `city_entities`: Comma-separated list of city entities (prefixed with `#Entities/City/`).
6. `person_entities`: Comma-separated list of person entities (prefixed with `#Entities/Person/`).

## 3. Markdown Navigation Indices

The six generated index files:
- **`Index - States.md`**: Alphabetical list of State tags (`#Entities/State/...`), with associated document links.
- **`Index - Cities.md`**: Cities grouped under their parent States (extracted from `#Entities/City/<State>/<City>`).
- **`Index - Organizations.md`**: Alphabetical list of Organization tags (`#Entities/Org/...`), with links.
- **`Index - People.md`**: Alphabetical list of Person tags (`#Entities/Person/...`), with links.
- **`Index - Topics.md`**: Alphabetical list of Topics (`#Topics/...`), with links.
- **`Index - Tags.md`**: Alphabetical list of conceptual Tags (`#Tags/...`), with links.
