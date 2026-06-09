# Data Model: Metadata Correctness Fixes

## GeneratedDocumentEligibility

Represents whether a vault Markdown file is a generated document output eligible for resume counters, interlinking/finalization discovery, indexing inputs, and skipped-output registry updates.

**Fields**:
- `path`: Candidate Markdown path.
- `vault_root`: Root used to interpret hidden/system/template folders.
- `is_markdown`: True only for Markdown files.
- `is_generated_document`: True only when all exclusion rules pass.
- `exclusion_reason`: Optional reason for ineligible files.

**Validation rules**:
- Exclude files named `Index - *.md`.
- Exclude vault landing/support `index.md` files.
- Exclude `metadata_index.xlsx` and other non-Markdown files by type.
- Exclude `.filtered.md` sidecars.
- Exclude hidden/system folder paths, including folders whose component starts with `.`.
- Exclude template files/folders and other known generated vault support files.
- Treat only eligible generated document Markdown as counter sources.

## ResumeCounterState

Reconstructed canonical tag counters derived from eligible generated document outputs.

**Fields**:
- `conceptual_tag_counts`: Counter of canonical conceptual tag paths from `#Tags/...`.
- `topic_counts`: Counter of canonical topics from `#Topics/...`.
- `entity_counts`: Counters grouped by `State`, `Org`, `City`, and `Person` from `#Entities/...`.
- `scanned_files_tags`: Mapping of generated document output paths to parsed canonical tags.

**Validation rules**:
- Every eligible generated document output may be counted at most once.
- Skip handling must not add a file already present in `scanned_files_tags`.
- If a skipped output is absent from `scanned_files_tags`, it must be parsed and registered once.
- Excluded support files must never enter the state.

## TaggingReuseHints

Compact preferred vocabulary passed from rebuilt counters to tagging.

**Fields**:
- `preferred_conceptual_tags`: Top conceptual counter path values for `#Tags` extraction.
- `preferred_entities`: Top entity values grouped by entity type.
- `preferred_topics`: Top topic counter values, subordinate to taxonomy choices.

**Validation rules**:
- Conceptual hints guide conceptual tag selection only.
- Entity hints guide entity extraction only.
- Topic hints cannot override the configured taxonomy.
- Hints are bounded to compact top-N lists suitable for prompt context.

## TaggingQualityPolicy

Rules that determine whether a parsed tagging result is acceptable.

**Fields**:
- `is_substantive`: Deterministic classification for the cleaned source.
- `minimum_conceptual_tags`: Five for substantive documents.
- `allow_empty_conceptual_tags`: True only for non-substantive administrative stubs.
- `quality_error`: Explicit failure reason when the result is unacceptable.

**Validation rules**:
- Substantive documents require `conceptual_tags` to be present and contain at least five items before duplicate suppression can erase useful tags.
- Non-substantive classification must be deterministic and conservative.
- Short length alone does not make a source non-substantive.
- Uncertain sources are substantive.
- Missing, omitted, empty, or undersized conceptual tags for substantive sources produce an explicit tagging-quality failure.

## ConceptualTagSet

Canonical conceptual tag paths generated for the `## Tags` section.

**Fields**:
- `raw_llm_values`: Values returned by the tagging call.
- `normalized_values`: Canonical normalized tag components.
- `filtered_values`: Values after low-value filtering.
- `suppressed_values`: Values after exact duplicate suppression.

**Validation rules**:
- Static useful-tags vocabulary and resume-derived conceptual counters are preferred vocabulary.
- New canonical conceptual tag paths are allowed when justified by source text.
- Hierarchical conceptual tags such as `#Tags/WINTEX/73` are valid and must preserve the full path.
- Exact duplicates of entity names or topic components may be suppressed.
- Substantive archival concepts, useful acronyms, exercise names, and protected preferred-vocabulary paths must be preserved when justified by source text.

## MirroredSourcePdf

Source PDF mirrored for a generated Markdown output.

**Fields**:
- `source_pdf_path`: Original PDF path associated with the source document.
- `generated_markdown_path`: Generated Markdown output path.
- `mirrored_pdf_path`: Output PDF path under the generated Markdown path's local `pdf/` subdirectory.
- `source_link`: Relative wikilink from the generated Markdown file to the mirrored PDF.

**Validation rules**:
- Mirrored PDFs are placed beside their generated Markdown output in a local `pdf/` directory.
- A nested generated document such as `.../1973/NPG-D(73)11_FRE.md` mirrors to `.../1973/pdf/NPG-D(73)11_FRE.pdf`.
- The generated Markdown source link remains relative, for example `[[pdf/NPG-D(73)11_FRE.pdf]]`.
- Dry-run must not create, copy, or hardlink mirrored PDFs.

## CanonicalIndexEntry

Production index/export entry populated from canonical data only.

**Fields**:
- `doc_path`: Vault-relative generated document path.
- `frontmatter`: Existing frontmatter metadata.
- `canonical_tags`: Parsed canonical tags.
- `export_columns`: Spreadsheet/index columns derived from canonical tags.

**Validation rules**:
- Only canonical `#Tags/...`, `#Topics/...`, and `#Entities/...` populate canonical columns.
- Obsolete unprefixed tags may be ignored or reported.
- Obsolete tags must not be migrated into canonical columns during index or XLSX generation.

## MetadataRunSafety

User safety controls for metadata command execution.

**Fields**:
- `mask`: Markdown glob used to select enrichment candidates.
- `dry_run`: Whether the run is non-mutating.
- `matching_markdown`: Markdown files eligible for enrichment.
- `mirrored_files`: Files mirrored only when not dry-run and when mirroring is intentional, including per-folder source PDFs.
- `planned_actions`: Dry-run report of work that would occur.

**Validation rules**:
- Only matching Markdown files are sent to metadata or tagging enrichment.
- `.filtered.md` sidecars are never enriched.
- Nonmatching Markdown files may be mirrored only when source-tree mirroring is intentionally enabled and dry-run is false.
- Dry-run creates, updates, copies, hardlinks, and initializes nothing.
