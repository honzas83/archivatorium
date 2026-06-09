# Phase 0: Research

## Zotero Export Format
- **Decision**: Use "Better CSL-JSON" format.
- **Rationale**: It conforms strictly to the predictable CSL-JSON schema (allowing the use of the standard Python `json` library) while naturally embedding the citation key inside the `id` attribute, which is exactly what is needed for matching documents by citekey.
- **Alternatives considered**: Standard CSL-JSON (lacks explicit citation keys), Better BibTeX JSON (an internal raw dump used for debugging, not interoperability).

## Parsing and Chicago Style Field Extraction
- **Decision**: Use Python's built-in `json.load()` to parse the Better CSL-JSON and extract standard fields (author, title, publisher, publisher-place, issued date, container-title, page, URL, type) to assemble a Chicago-style citation callout.
- **Rationale**: Using the standard library avoids adding unnecessary external dependencies. The Better CSL-JSON structure is a simple JSON array of objects where the `id` maps to the citekey, making extraction straightforward.
- **Alternatives considered**: Using a specialized BibTeX parsing library (like `pybtex`), but this is unnecessary given Zotero's ability to export to a standard JSON schema.
