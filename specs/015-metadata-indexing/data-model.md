# Data Model: Metadata Indexing

## Index Entry
Represents a single document's metadata extracted for the index.

| Field | Type | Description |
|-------|------|-------------|
| doc_path | Path | Path to the source `.md` file. |
| title | str | Document title from frontmatter. |
| summary | str | One-sentence summary. |
| date | str | ISO date. |
| entities | list[EntityReference] | All extracted hierarchical tags. |
| raw_metadata | dict | Full frontmatter parsed into a dictionary. |

## Entity Reference
Represents a specific tag found in a document.

| Field | Type | Description |
|-------|------|-------------|
| prefix | str | Top-level hierarchical component (e.g., "State"). |
| value | str | The full tag string (e.g., "#State/Belgium"). |
| label | str | The display label (e.g., "Belgium"). |

## Topic Hierarchy (from YAML)
Loaded from the provided topics YAML.

| Field | Type | Description |
|-------|------|-------------|
| category | str | Main category name (e.g., "Doctrine-and-Strategy"). |
| topic | str | Sub-topic name (e.g., "Extended-Deterrence"). |
| description | str | Detailed explanation of the topic. |
