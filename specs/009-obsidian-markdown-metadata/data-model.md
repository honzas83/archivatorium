# Data Model: Obsidian Metadata

This document describes the flattened metadata structure used for Obsidian compatibility.

## ObsidianMetadata

The following fields are extracted and stored in the YAML frontmatter of the Markdown file.

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Formal title of the document. |
| `summary` | string | Two-sentence summary. |
| `abstract` | string | Detailed overview (up to 20 sentences). |
| `author_name` | string | Name of the author. |
| `author_institution` | string | Organization of the author. |
| `date` | string (ISO 8601) | Document date (YYYY-MM-DD). |
| `archive_code` | string | Primary archive reference. |
| `language` | string | Document language. |
| `location_city` | string | Origin city. |
| `location_state` | string | Origin nation-state. |
| `correspondence_sender` | string | Sender of correspondence (if applicable). |
| `correspondence_recipient` | string | Recipient of correspondence (if applicable). |
| `correspondence_transaction` | string | Purpose of correspondence (if applicable). |
| `mentioned_states` | list[string] | Nation states mentioned. |
| `mentioned_organisations` | list[string] | Organizations mentioned. |
| `references` | list[string] | Other archive references mentioned. |
| `tags` | list[string] | Obsidian tags (without `#` prefix). |
| `source` | string | Obsidian link to source PDF using relative path, e.g., `[[PDFs/filename.pdf]]`. |

## Validation Rules
- `tags` must not contain spaces.
- `date` must follow YYYY-MM-DD format.
- `source` must be formatted as an Obsidian internal link with a relative path if applicable.
