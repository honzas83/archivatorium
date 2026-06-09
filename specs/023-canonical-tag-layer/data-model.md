# Data Model: Canonical Tag Layer

This document defines the structured tag model and validation schemas for canonical generated tags in OCRPolish.

---

## 1. Structured Tag Model (`CanonicalTags`)

The `CanonicalTags` model represents the structured, normalized tags parsed from a Markdown document.

### Schema Fields

| Field Name | Type | Description |
|---|---|---|
| `conceptual_tags` | `set[str]` | Normalized conceptual tag paths, excluding the leading `#Tags/` prefix. |
| `topics` | `set[str]` | Normalized topic paths, excluding the leading `#Topics/` prefix. |
| `entities` | `dict[str, set[str]]` | Map of entity types to sets of normalized paths, excluding `#Entities/<type>/`. Supported types: `State`, `Org`, `City`, `Person`. |
| `raw_paths` | `set[str]` | Complete normalized tag paths (e.g., `Entities/State/France`) without leading `#` to allow full reconstruction. |

### Validation & Normalization Constraints

- **Component Normalization**: Every path component (parts separated by `/`) is normalized using `normalize_tag_component`:
  - Non-alphanumeric characters replaced by hyphens.
  - Collapsed multiple hyphens.
  - Preserved original casing.
- **Valid Entity Types**: Supported keys in `entities` are strictly limited to `"State"`, `"Org"`, `"City"`, and `"Person"`.
- **City Tags**: Must contain exactly 4 components: `Entities/City/<State>/<City>`.
- **State/Org/Person Tags**: Must contain exactly 3 components: `Entities/<Type>/<Name>`.
- **Topic Tags**: Must contain at least 2 components: `Topics/<taxonomy-path>`.
- **Conceptual Tags**: Must contain exactly 2 components: `Tags/<tag>`.

---

## 2. Global Tag Counters (`TagCounters`)

Used to track tag frequencies during directory execution and vault indexing.

### Schema Fields

| Field Name | Type | Description |
|---|---|---|
| `conceptual_tag_counts` | `Counter[str]` | Tracks occurrences of each normalized conceptual tag (without `#Tags/`). |
| `topic_counts` | `Counter[str]` | Tracks occurrences of each normalized topic path (without `#Topics/`). |
| `entity_counts` | `dict[str, Counter[str]]` | Tracks entity occurrences grouped by entity type (State, Org, City, Person). |

---

## 3. Parsing Diagnostics (`ParseDiagnostic`)

Represents warning diagnostics generated during the parsing pass.

### Schema Fields

| Field Name | Type | Description |
|---|---|---|
| `file_path` | `Path` | Absolute path of the Markdown file being parsed. |
| `raw_tag` | `str` | The exact invalid tag string encountered. |
| `error_message` | `str` | Reason why the tag is considered invalid/malformed. |
