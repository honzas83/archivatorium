# Data Model: Simplify Metadata Pipeline

## MetadataCommandConfiguration

Represents the effective metadata command inputs after defaults are applied.

**Fields**:
- `input_dir`: Existing source directory scanned recursively.
- `output_dir`: Generated vault/output directory.
- `mask`: Markdown file glob, defaulting to `*.md`.
- `model`: Ollama model name.
- `hierarchy_file`: Required taxonomy YAML path.
- `tags_file`: Required useful tags YAML path.
- `vault_root`: Effective vault root; defaults to `output_dir` when omitted.
- `pdf_dir`: Effective source PDF lookup/root; defaults to `output_dir` when omitted for compatibility.
- `citekey_mode`: Existing deterministic citekey mode.
- `overwrite`: Whether existing generated Markdown is overwritten.
- `dry_run`: Whether writes are skipped.

**Validation rules**:
- `input_dir` must exist.
- `hierarchy_file` and `tags_file` must be explicitly provided and exist.
- Omitted `vault_root` resolves to `output_dir`.
- Omitted `pdf_dir` resolves to `output_dir`.
- No production option may select non-flat topic extraction.

## MirroredPdfReference

Represents the generated PDF copy/link relationship for a source document.

**Fields**:
- `source_pdf`: PDF found through the production lookup process.
- `output_pdf`: Mirrored PDF path under the generated vault's `pdf/` directory for the output Markdown location.
- `obsidian_link`: Vault-relative source link in the form `[[pdf/<filename>.pdf]]`.

**Validation rules**:
- `output_pdf` must be inside a `pdf/` directory in the generated output layout.
- `obsidian_link` must be derived from `output_pdf`, not from the input lookup directory.
- Ambiguous filename collisions must be resolved or reported before writing an ambiguous source link.

## FileProcessingPipeline

Represents one complete metadata processing run for a single source Markdown file.

**Stages**:
1. `read_source`: Input path to raw source text.
2. `parse_source_and_strip_generated_sections`: Raw source text to existing frontmatter plus clean body text.
3. `extract_document_metadata`: Clean text plus filename/context to extracted document metadata.
4. `extract_generated_tags`: Clean text to flat tagging result.
5. `reconcile_metadata_and_tags`: Existing metadata, extracted metadata, computed fields, and generated tags to reconciled output.
6. `render_frontmatter`: Reconciled output to YAML frontmatter.
7. `render_callouts`: Reconciled output and clean body to Metadata, Abstract, and Citation callouts.
8. `write_output`: Rendered output to output Markdown path.
9. `ingest_generated_output_tags`: Written output content to global tag/entity/topic counters.

**Validation rules**:
- Each stage has explicit inputs and outputs that can be asserted independently in tests.
- Full pipeline output preserves compatible observable output behaviour.
- Generated-output tag ingestion occurs after output content is produced.

## FlatTaggingPromptContext

Represents static and dynamic prompt data used by production tagging.

**Fields**:
- `normalized_themes`: Loaded and normalized taxonomy data.
- `flattened_taxonomy`: Flat taxonomy computed once per tagging service instance.
- `taxonomy_prompt_text`: Static serialized taxonomy prompt section.
- `useful_tags`: Loaded and normalized useful tag values.
- `useful_tags_prompt_text`: Static useful-tags prompt section.
- `window_text`: Per-window document text.

**Validation rules**:
- `flattened_taxonomy`, `taxonomy_prompt_text`, and `useful_tags_prompt_text` are computed once during tagging service initialization.
- Per-window prompt generation reuses static prompt text and only varies by document window text.
- Production topic tags use flat `Category/Topic` format.

## LegacyTopicEvaluationArtifact

Represents optional retained historical evaluation code.

**Fields**:
- `path`: Location outside `ocrpolish/`.
- `purpose`: Evaluation or comparison only.
- `production_imports`: Must not be required by production metadata processing.

**Validation rules**:
- Must not define selectable production behaviour.
- Must not be imported by `ocrpolish.cli`, `ocrpolish.processor_metadata`, or production tagging services.
- Must not be part of production behaviour tests.
