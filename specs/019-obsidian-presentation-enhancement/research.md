# Research: Obsidian Presentation Enhancement

## Decision: Vault Initialization Location
- **Decision**: Implement vault initialization in `ocrpolish/cli.py` within the `metadata` command.
- **Rationale**: The `metadata` command is the entry point for generating Obsidian vaults. Initializing the vault settings before the file processing loop ensures that the output directory is correctly configured from the start.
- **Alternatives considered**: 
  - `MetadataProcessor.__init__`: Rejected because the processor should focus on document-level logic rather than vault-level infrastructure.
  - `IndexingService`: Rejected because indexing happens after metadata generation, and the vault should be configured before files are written.

## Decision: Metadata Table Implementation
- **Decision**: Create a new utility function `format_metadata_table(metadata_dict)` in `ocrpolish/utils/metadata.py`.
- **Rationale**: Centralizing the formatting logic in `utils/metadata.py` follows the existing pattern for citation and abstract callouts.
- **Icons**:
  - `≡&nbsp;`: title, summary, sender, recipient, intent, author_name, author_institution, archive_code, language, location_city, location_state
  - `№&nbsp;`: pages
  - `🗓&nbsp;`: date
  - `🔗&nbsp;`: source
  - `☰&nbsp;`: references

## Decision: BibTeX Format Update
- **Decision**: Modify `format_bibtex_citation` in `ocrpolish/utils/metadata.py`.
- **Rationale**: The user requested a single `date` field in `YYYY-MM-DD` format to replace separate `year`, `month`, and `day` fields. This improves compatibility with modern BibTeX parsers.

## Decision: Topic Citation Normalization
- **Decision**: Add a normalization step in `MetadataProcessor.process_file` after the tagging pass.
- **Rationale**: Normalizing the `reason` field for topics ensures that direct citations are consistently formatted as `_"citation"_`. Using regex for this transformation is efficient and can be applied directly to the extracted topic results.

## Unknowns Resolved
- **BibTeX Citekey**: The `ArchiveCode` (normalized) should continue to be used as the citekey.
- **Hidden Properties**: `app.json` will be set to hide properties by default, making the visual callout essential for user experience.
