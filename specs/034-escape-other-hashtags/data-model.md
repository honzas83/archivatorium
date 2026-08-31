# Data Model: Escaping and Indexing Structures

This document describes the in-memory data models and representation of files in the Obsidian vault.

## VaultDocument (In-Memory representation of Markdown files)

The system parses each markdown file in the Obsidian vault into a `VaultDocument` object.

### Fields and Schema
* **path**: `pathlib.Path`
  * Absolute path to the markdown file on disk.
* **vault_relative_path**: `str`
  * Path relative to the vault root directory (used for markdown links).
* **archive_code**: `str`
  * Unique document archive code (extracted from frontmatter).
* **language**: `str`
  * Document language (e.g. `English`, `French`).
* **frontmatter**: `dict[str, Any]`
  * Parsed YAML metadata from the top of the file.
* **raw_references**: `list[str]`
  * Unresolved document references.
* **canonical_tags**: `CanonicalTags`
  * Object representing parsed `#Entities`, `#Topics`, and `#Tags`.
* **body**: `str`
  * The markdown body content (excluding frontmatter).

---

## IndexEntry

An entry object used by the `IndexingService` to track and generate vault indices.

### Fields and Schema
* **doc_path**: `pathlib.Path`
  * Vault-relative path to the target document.
* **title**: `str`
  * The clean display title of the document.
* **canonical_tags**: `CanonicalTags`
  * The canonical tags parsed from the document.
