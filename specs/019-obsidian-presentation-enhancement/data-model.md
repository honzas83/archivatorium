# Data Model: Obsidian Presentation Enhancement

## Entities

### Obsidian Vault
- **Root Directory**: The base directory for processed documents.
- **.obsidian/app.json**: JSON file defining application settings (e.g., hiding properties).
- **.obsidian/appearance.json**: JSON file defining appearance settings (e.g., theme).
- **CONTENT.base**: A foundational markdown file placed in the root for navigation or metadata overview.

### Metadata Callout
- **Type**: `[!info]`
- **Title**: `Metadata`
- **Formatting**:
  - **Bold Labels**: `**title**`, `**pages**`, `**date**`.
  - **Bold Values**: Values for bolded labels are also bolded (e.g., `**10**`).
  - **Separate Lines**: List items (references) use `<br>` to render on new lines.
  - **Headerless**: The explicit header row is removed; the first field (**title**) is promoted to the technical header row to satisfy Markdown parsing requirements.
- **Fields**:
  - `title`: Document title (Icon: ≡)
  - `summary`: One-sentence summary (Icon: ≡)
  - `pages`: Total page count (Icon: №)
  - `source`: Link to PDF (Icon: 🔗)
  - `sender`: Sender (Icon: ≡)
  - `recipient`: Recipient (Icon: ≡)
  - `intent`: Intent (Icon: ≡)
  - `author_name`: Author (Icon: ≡)
  - `author_institution`: Institution (Icon: ≡)
  - `date`: Document date in `DD.MM.YYYY` format (Icon: 🗓)
  - `archive_code`: Reference code (Icon: ≡)
  - `language`: Language (Icon: ≡)
  - `location_city`: City (Icon: ≡)
  - `location_state`: State (Icon: ≡)
  - `references`: List of related documents (Icon: ☰)

### Citation Callout
- **Type**: `[!citing this document]`
- **Formats**:
  - **Chicago**: Text-based citation.
  - **Harvard**: Text-based citation.
  - **BibTeX**: Updated `@misc` block with `date = {YYYY-MM-DD}`.

### Normalized Topic
- **Topic**: Hierarchical tag (e.g., `#Category/Topic`).
- **Reason**: Descriptive text where all quotes (single or double) around direct citations are converted to `_"text"_`.

## Relationships
- **Vault** contains many **Markdown Files**.
- **Markdown File** contains exactly one **Metadata Callout**, one **Abstract Callout**, and one **Citation Callout**.
- **Abstract Callout** contains many **Normalized Topics**.
