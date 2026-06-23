# OPTIMISATION-v0

Date: 2026-06-08

Scope: source, tests, specs, and docs for the current metadata/tagging/interlinking pipeline. Generated vault/export trees were not audited except as context.

Current command being audited before simplification:

```text
python -m archivatorium.cli metadata NATO_NPG_source NATO_NPG_metadata.v5 --model gemma4:31b --pdf-dir NATO_NPG_metadata.v5/ --vault-root NATO_NPG_metadata.v5 --hierarchy-file topics/NATO_themes.yaml --tags-file topics/USEFUL_TAGS.yaml --flat-topics
```

The audit assumes this is the current workflow that should be simplified. Other metadata variants are out of scope and should be removed rather than preserved as first-class paths.

Confirmed product decisions:

- Non-flat topic extraction should be removed.
- `#Entities/...`, `#Topics/...`, and `#Tags/...` are the authoritative outputs.
- On resume after interruption, scan generated outputs first, rebuild counters, then continue.
- Generated PDFs are always mirrored into `pdf/`.
- `--hierarchy-file` and `--tags-file` should remain required command options.
- XLSX should pivot to the canonical generated tag model.
- For the `summary` field, use the sentence count implemented in code: exactly one sentence.
- Generate a `citekey` frontmatter field from the output filename, not from `archive_code`. The default key source should be the filename stem; an optional mode may use the full vault-relative path without the `.md` suffix for stronger disambiguation. The final key must use safe BibTeX characters.

Superseded historical specs:

- `specs/008-ollama-metadata-extraction`: the general `metadata` command, recursive processing, alphabetical processing, schema-enforced Ollama extraction, and deterministic metadata merging remain relevant. Run-wide consistency from tag frequency remains relevant, but the source of counters changes from legacy metadata tags to canonical generated tags. The old `gemma4:26b` optimization note is superseded by the production `gemma4:31b` workflow.
- `specs/009-obsidian-markdown-metadata`: Markdown output, top-level YAML frontmatter, flattened keys, and source links remain relevant. Any interpretation that stores generated tags in YAML frontmatter is superseded by the Abstract-callout generated tag model. Its two-sentence summary data-model wording is superseded by the current code-level one-sentence rule.
- `specs/010-refine-obsidian-metadata`: removing `abstract` from YAML frontmatter and rendering it in an `[!abstract]` callout remains relevant. Its single-sentence `summary` rule overrides the older two-sentence rule in `specs/008` because the current prompt and `MetadataSchema` already implement exactly one sentence.
- `specs/011-llm-topic-extraction`: superseded for production by flat topic extraction. The two-step/non-flat `TopicExtractor` path should be removed from runtime.
- `specs/012-llm-flat-topic-extraction`: remains relevant and becomes the only production topic extraction mode. The flattened hierarchy should be cached once and reused. Accuracy-comparison requirements against the removed two-step extractor are superseded for production implementation.
- `specs/014-obsidian-export-enhancement`: entity extraction via `mentioned_*` fields is superseded by generated `#Entities/...` tags. The older requirement to convert `mentioned_*` into unprefixed `#State/...`, `#Org/...`, and `#City/...` tags no longer defines production behaviour. Its last-page-header page-count rule is superseded by `specs/022` header-count behaviour. Older `transaction`/`correspondence` naming is superseded by `intent`.
- `specs/015-metadata-indexing`: XLSX/indexing requirements based on `MetadataSchema.model_fields` and unprefixed `#State/...`, `#City/...`, `#Org/...`, `#Category/...` tags are superseded by canonical generated tag parsing. Its `index INPUT_DIR --output-xlsx` and current `index INPUT_DIR OUTPUT_DIR` CLI shapes are superseded by the production `interlink VAULT_DIR` finalization command. Indexing should be merged with interlinking as one idempotent vault-finalization workflow rather than remaining a separate vault scan.
- `specs/016-metadata-citations`: citation callout generation remains relevant and should be preserved by the pipeline refactor. Its requirement to use `archive_code` as the BibTeX citekey is superseded by deterministic `citekey` generation from the output filename or optional vault-relative path.
- `specs/017-preserve-metadata-structure`: mirrored directory structure, hardlink/copy fallback, `pdf/` storage, and source-link updates remain relevant.
- `specs/018-tagging-system`: the second-pass tagging model, entity/topic/conceptual separation, duplicate suppression, sliding-window fallback, and useful-tags/taxonomy inputs remain relevant. Its feedback-loop requirement based on mentioned states/organisations/cities is superseded by generated-tag counters rebuilt from `#Entities/...`, `#Topics/...`, and `#Tags/...`.
- `specs/019-obsidian-presentation-enhancement`: vault initialization, Metadata callout presentation, citations, topic-reason normalization, and tag casing guidance remain relevant. Its wording that the Abstract callout contains summary and mentioned entities is superseded by the generated Abstract callout model: abstract text plus generated topics/entities/tags.
- `specs/020-obsidian-interlink-vault`: remains relevant and defines the production command name: `interlink`. Interlinking must not mutate YAML frontmatter. Any filename-only mapping wording is superseded by the full vault-relative path requirement. The `interlink` command should run reference interlinking before index/XLSX generation inside the shared idempotent vault-finalization workflow.
- `specs/021-tag-grouping-prefixes/spec.md`: singular examples such as `#Topic/...` and `#Entity/...` should be read through the configured plural constants currently used by the plan/code: `#Topics/...`, `#Entities/...`, and `#Tags/...`.
- `specs/022-fix-interlink-pages-timeout`: archive-code normalization, header-based page counting, and Ollama timeout behaviour remain relevant.

Agreed consistency model:

```text
existing generated outputs -> canonical tag parser -> counters/context
source markdown only       -> metadata LLM + tagging LLM
metadata + tags            -> deterministic reconciliation/rendering
rendered output            -> ingest canonical tags for the next file
```

Generated metadata must not be fed back into LLM prompts. Cross-document consistency should come from compact, canonical context rebuilt from generated tags (`#Entities/...`, `#Topics/...`, `#Tags/...`), not from prior summaries, abstracts, citation blocks, metadata tables, or old frontmatter fields.

This does not forbid preserving or merging legitimate user/frontmatter metadata. It means generated frontmatter, generated callouts, generated citations, and prior generated abstracts must be excluded from LLM context; any preserved metadata should be merged and rendered deterministically after extraction.

Rendered metadata consistency contract:

- YAML frontmatter and the generated Metadata table/callout must match for canonical document metadata fields: `title`, `summary`, `pages`, `source`, `sender`, `recipient`, `intent`, `author_name`, `author_institution`, `date`, `archive_code`, `citekey`, `language`, `location_city`, and `location_state`.
- Raw `references` are canonical document metadata and may be stored in YAML frontmatter as archive-code strings. The Metadata table starts as a rendered view of those raw references, then interlinking may enrich the table with linked references and `language_versions` without mutating YAML frontmatter.
- The Metadata table is a rendered presentation layer. It may include deterministic derived navigation fields such as enriched `references` or `language_versions` links, but those fields must be explicitly derived rather than accidentally drifting from frontmatter.
- Generated tags/entities/topics must not be stored as frontmatter `tags` or table-only legacy fields. Their authoritative representation is the generated `#Entities/...`, `#Topics/...`, and `#Tags/...` syntax.
- Extra frontmatter fields outside the canonical document metadata set should either be removed from production output or deliberately added to the Metadata table mapping. Hidden frontmatter-only fields make XLSX/index/resume behaviour harder to reason about.
- Generated `source` values must use the mirrored PDF layout, e.g. `[[pdf/<filename>.pdf]]`.

## Executive summary

The biggest avoidable cost is duplicated LLM work in `metadata`: the primary metadata pass still asks for legacy `mentioned_states`, `mentioned_organisations`, `mentioned_cities`, and flat `tags`, even when `TaggingService` is enabled and fully replaces those values with `entity_tags`, `topic_tags`, and `conceptual_tags`.

The largest likely bug is that indexing expects unprefixed tags such as `#State/Belgium`, but current generated metadata uses root-prefixed tags such as `#Entities/State/Belgium`, `#Topics/...`, and `#Tags/...`. This can make generated state/city/org/topic indices empty or incomplete for generated vault output.

Resume after interruption is not consistency-safe today. Already generated files are skipped, but their tags/entities are not read back into `tag_counts`, `state_counts`, `org_counts`, or `city_counts`, so resumed processing starts with empty or partial consistency context.

Frontmatter and the generated Metadata table/callout are only partially consistent today. They are initially rendered from the same metadata dictionary for common fields, but the table is a fixed projection and postprocessing can enrich table fields such as `references` without updating YAML frontmatter. This should become an explicit contract rather than accidental divergence.

Focused tests around metadata, tagging, indexing, and interlinking pass, but the tests mostly validate legacy/unprefixed indexing shapes and do not cover several current CLI behaviours.

## High priority

### 1. Remove obsolete `mentioned_*` and legacy flat-tag fields from the normal path

Evidence:

- `MetadataSchema` still contains `mentioned_states`, `mentioned_organisations`, `mentioned_cities`, and legacy `tags` in `archivatorium/models/metadata.py`.
- `MetadataProcessor.process_file()` always prompts for those fields in rules 4-6 and 14, then calls `extract_structured(prompt, MetadataSchema)`.
- If `self.tagging_service` exists, current output entities/topics/tags are generated from `tagging_result`, not from those legacy fields.
- The legacy fields are removed from frontmatter by `_prepare_obsidian_metadata()`.
- Product decision: `#Entities/...`, `#Topics/...`, and `#Tags/...` are authoritative.

Impact:

- Wastes prompt tokens and model attention on fields that are thrown away in the normal production path.
- Adds hallucination surface: the first pass may invent cities/states/orgs that are later unused but still update cross-document counters.
- The counters (`state_counts`, `org_counts`, `city_counts`) continue to bias later prompts with legacy entities, even though the precision tagging pass is authoritative.

Recommendation:

- Replace `MetadataSchema` in the normal path with a lean document metadata schema that excludes `mentioned_states`, `mentioned_organisations`, `mentioned_cities`, and legacy `tags`.
- Remove prompt rules for `mentioned_*` and legacy flat `tags`.
- Stop updating `state_counts`, `org_counts`, and `city_counts` from legacy fields.
- Update consistency context from canonical `tagging_result.entity_tags` and `tagging_result.conceptual_tags`.
- Do not implement legacy tag import or migration in the production path.

### 2. Pivot indexing and XLSX to the canonical generated tag model

Evidence:

- `TAG_PREFIX_ENTITY = "Entities"`, `TAG_PREFIX_TOPIC = "Topics"`, and `TAG_PREFIX_TAG = "Tags"` in `archivatorium/data_model.py`.
- `MetadataProcessor` writes entities with `prefix_tag(e, TAG_PREFIX_ENTITY)`, producing tags like `#Entities/State/United-Kingdom`.
- `IndexingService.INDEX_PREFIXES` only includes `State`, `City`, `Org`, and `Category`.
- `_parse_entity()` reads `parts[0]` as the prefix, so `#Entities/State/UK` is rejected because `Entities` is not in `INDEX_PREFIXES`.
- Tests still validate `#State/...`, `#City/...`, and `#Org/...`, not current generated `#Entities/...`.
- `generate_xlsx()` exports columns from `MetadataSchema.model_fields`, which still includes old `mentioned_*` fields and omits grouped tag/entity/topic columns from the generated tag model.
- Product decision: XLSX should pivot to the canonical generated tag model.

Impact:

- `archivatorium index` can miss all generated entity tags and produce empty `Index - States.md`, `Index - Cities.md`, and `Index - Organizations.md`.
- Topic indexing can similarly miss `#Topics/...` unless a legacy topic prefix happens to match.
- XLSX currently preserves obsolete schema columns instead of showing the authoritative `Entities`, `Topics`, and `Tags`.

Recommendation:

- Teach `IndexingService` to strip known root prefixes before parsing, e.g. `Entities/State/... -> State/...`, `Topics/Category/... -> Category/...`.
- Add tests that process a generated-style abstract callout containing `#Entities/State/Belgium`, `#Entities/City/Belgium/Brussels`, `#Entities/Org/NATO`, and `#Topics/Category/...`.
- Replace schema-field XLSX export with generated-tag-model columns such as:
  - core metadata: file path, title, summary, pages, date, archive_code, citekey, language, source
  - entities: states, cities, organisations, people
  - topics
  - conceptual tags
- Do not keep old `mentioned_*` columns in production XLSX export.

### 3. Rebuild tag/entity counters when resuming after interruption

Evidence:

- `MetadataProcessor.__init__()` initializes `tag_counts`, `state_counts`, `org_counts`, and `city_counts` as empty in-memory counters.
- The CLI computes `frequent_tags` from `processor.tag_counts.most_common(50)` immediately before each `process_file()` call.
- `process_file()` returns early when `output_file.exists()` and `overwrite` is false.
- That early return happens before reading the existing generated output, parsing frontmatter, or extracting abstract callout tags.
- Existing generated outputs contain the authoritative generated tags in the abstract callout (`#Entities/...`, `#Topics/...`, `#Tags/...`), but those are not loaded into counters before processing remaining files.

Impact:

- If the production command is interrupted and run again, skipped files do not contribute to tag reuse context.
- The resumed batch may create less consistent flat conceptual tags because `frequent_tags` is missing prior generated tags.
- Entity consistency context is also missing. Since counters should move to generated entity tags, resume support must read those tags from existing output first.

Recommendation:

- Add a preflight scan of `output_dir` before processing new files:
  - Parse existing generated `.md` files.
  - Ignore old frontmatter `tags`.
  - Read abstract callout tags via `extract_abstract_tags()`.
  - Strip root prefixes and update counters from `#Tags/...`, `#Entities/State/...`, `#Entities/Org/...`, and `#Entities/City/...`.
- Alternatively, when an output file exists and is skipped, process it through a lightweight `ingest_existing_output(output_file)` path before continuing.
- Add an integration test:
  1. Run/process one file and write generated output containing `#Tags/NATO`, `#Entities/State/France`, and `#Entities/Org/NATO`.
  2. Create a new `MetadataProcessor` with the same output directory, simulating a fresh resumed process.
  3. Process a second file without `--overwrite`.
  4. Assert the second file's metadata prompt receives `frequent_tags` or vocabulary context derived from the first generated output.

### 4. Specialize CLI defaults to the production workflow

Evidence:

- Current production command always passes:
  - `--model gemma4:31b`
  - `--pdf-dir <output_dir>`
  - `--vault-root <output_dir>`
  - `--hierarchy-file topics/NATO_themes.yaml`
  - `--tags-file topics/USEFUL_TAGS.yaml`
  - `--flat-topics`
- `--flat-topics` is currently opt-in, although this is the only planned topic mode.
- `--pdf-dir` and `--vault-root` duplicate the output directory in the current workflow.
- `--hierarchy-file` and `--tags-file` should remain explicit because changing taxonomy/vocabulary is semantically important.
- Generated PDFs are always mirrored into `pdf/`, so source-link defaults should match that layout.
- The default model in `OllamaClient` is `gemma4:26b`, while the CLI default is `gemma4:31b`.

Impact:

- The normal command is unnecessarily long and easy to run with one missing option.
- Non-flat topic mode and missing taxonomy/tag files are still treated as common paths, which keeps obsolete branching and tests alive.
- Requiring `--pdf-dir` and `--vault-root` to equal the output directory creates avoidable user error.
- If `pdf_dir` points at `output_dir` but links expect root-level PDFs, links may not match the actual `pdf/` mirror layout.

Recommendation:

- Remove non-flat topic mode from the production code path.
- Make flat topic extraction unconditional when `--hierarchy-file` and `--tags-file` are provided.
- Default `pdf_dir` to `output_dir` when omitted.
- Default `vault_root` to `output_dir` when omitted.
- Ensure generated `source` links point to `[[pdf/<filename>.pdf]]` for mirrored PDFs.
- Keep `--hierarchy-file` and `--tags-file` explicit inputs.
- Fail fast if either `--hierarchy-file` or `--tags-file` is omitted.
- Align `OllamaClient` and CLI defaults around `gemma4:31b`.
- After those changes, the production command should become:

```text
python -m archivatorium.cli metadata NATO_NPG_source NATO_NPG_metadata.v5 --hierarchy-file topics/NATO_themes.yaml --tags-file topics/USEFUL_TAGS.yaml
```

or, if keeping explicit model selection:

```text
python -m archivatorium.cli metadata NATO_NPG_source NATO_NPG_metadata.v5 --model gemma4:31b --hierarchy-file topics/NATO_themes.yaml --tags-file topics/USEFUL_TAGS.yaml
```

### 5. `metadata --mask` is ignored for Markdown enrichment

Evidence:

- CLI metadata command calls `processor.get_files(input_dir, mask=mask, all_files=True)`.
- With `all_files=True`, `get_files()` returns every file and does not apply `mask`.
- The CLI loop enriches every non-filtered `.md` file regardless of `mask`.
- `MetadataProcessor.process_directory()` has the same pattern.

Impact:

- `archivatorium metadata input output --mask 'NPG*.md'` still sends every Markdown file to Ollama.
- This is both expensive and surprising.

Recommendation:

- Mirror all files if desired, but only enrich Markdown files that match `mask`.
- Add a regression test with two `.md` files and a restrictive mask.

Note: This matters less for the current production command if `--mask` will not be used, but it is still a correctness trap in the CLI surface.

### 6. Define frontmatter and Metadata table consistency

Evidence:

- `process_file()` renders frontmatter and the Metadata callout from the same `metadata_dict` during initial generation.
- `format_metadata_table()` renders only a fixed list of mapped fields, so extra frontmatter fields can be present without appearing in the table.
- The `abstract` and `tags` values are removed from `metadata_dict` before frontmatter/table rendering, which is correct for the current generated tag model.
- Interlinking can enrich rendered table fields such as `references` or `language_versions` while leaving YAML frontmatter unchanged.
- Generated files can therefore have matching core fields but different `references` values between frontmatter and the rendered Metadata table.

Impact:

- Consumers cannot tell whether the Metadata table is intended to be a copy of frontmatter or a derived rendered view.
- XLSX/index/resume logic can accidentally choose the wrong source of truth.
- Table/frontmatter drift makes it harder to validate generated output after interruption or postprocessing.

Recommendation:

- Treat YAML frontmatter as canonical for document metadata fields.
- Treat the Metadata table as a deterministic rendered view over canonical frontmatter plus explicitly derived navigation fields.
- Require exact semantic agreement between frontmatter and the table for canonical document metadata fields.
- Permit table-only derived navigation fields only when they are generated by a named deterministic step, e.g. interlinking-derived references or language versions.
- Do not store generated `#Entities/...`, `#Topics/...`, or `#Tags/...` in frontmatter/table metadata fields.
- Add a regression test that renders a document, runs interlinking, and asserts:
  - canonical document metadata fields remain consistent between YAML and the Metadata table
  - derived navigation fields are either present in both layers by design or explicitly table-only
  - `source` points to `[[pdf/<filename>.pdf]]`

### 7. Generate BibTeX citekeys from output filenames, not archive codes

Evidence:

- `format_bibtex_citation()` currently computes the `@misc{...}` key with `safe_identifier(data.get("archive_code", ""))`.
- `format_chicago_citation()` and `format_harvard_citation()` also compute default URLs from the safe archive code. Those URL defaults are related but separate from the BibTeX citekey decision.
- `generate_citation_callout()` receives only the metadata dictionary passed from `MetadataProcessor.process_file()`.
- `process_file()` currently appends citations after rendering frontmatter/callouts, but it does not add any filename-derived citation key to metadata.
- `MetadataSchema` does not contain `citekey`.
- `_prepare_obsidian_metadata()` does not create `citekey`, and `format_metadata_table()` does not render it.
- `safe_identifier()` already normalizes strings to safe BibTeX/URL characters: letters, digits, hyphen, underscore, and colon.
- `InterlinkingService` uses `safe_identifier(archive_code)` as a fuzzy archive-code matching fallback. That is not the same thing as the citation BibTeX citekey and should remain tied to archive-code resolution unless explicitly redesigned.

Impact:

- Two documents with the same extracted `archive_code` can produce duplicate BibTeX citekeys.
- OCR or LLM errors in `archive_code` can change the BibTeX citekey even when the output filename is stable.
- The generated citekey is not visible in frontmatter, so later exports cannot reliably reuse the same key without reparsing the citation callout.

Recommendation:

- Add a deterministic `citekey` metadata field during rendering/reconciliation, not via the LLM schema.
- Default key source: output filename stem, e.g. `NPG(STUDY)38_ENG.md -> NPG-STUDY-38_ENG`.
- Optional disambiguating key source: vault-relative output path without `.md`, e.g. `NPG - Nuclear Planning Group/3 NPG(STUDY)/NPG(STUDY)38_ENG -> NPG-Nuclear-Planning-Group-3-NPG-STUDY-NPG-STUDY-38_ENG`.
- Always pass the chosen key source through `safe_identifier()`.
- Store the final safe value in YAML frontmatter as `citekey`.
- Render `citekey` in the Metadata table so the table remains consistent with frontmatter.
- Make `format_bibtex_citation()` use `data["citekey"]` when present and fall back to `safe_identifier(filename_stem)` only in direct utility calls/tests. It should not derive the BibTeX citekey from `archive_code`.
- Keep `archive_code` in Chicago/Harvard note text and BibTeX `note`; only the BibTeX citekey source changes.
- Decide separately whether citation URLs should continue to default to archive-code-based URLs or move to filename-derived URLs. The current request only changes the BibTeX citekey.
- Update tests:
  - unit test for `safe_identifier()` on filename/path examples
  - unit test that `format_bibtex_citation()` uses `citekey` instead of `archive_code`
  - integration test that processed output contains the same generated citekey value in frontmatter, the Metadata table, and the BibTeX `@misc{...}` entry

Affected code paths:

- `archivatorium/utils/metadata.py`
  - `safe_identifier()` can be reused for filename/path key normalization.
  - `format_bibtex_citation()` currently uses `archive_code`; change to `citekey`.
  - `generate_citation_callout()` should receive metadata that already includes `citekey`.
  - `format_metadata_table()` should include a `citekey` row.
- `archivatorium/processor_metadata.py`
  - `process_file()` has both `input_file` and `output_file`; generate `citekey` after the final `.md` output path is known and before frontmatter/table/citation rendering.
  - `_prepare_obsidian_metadata()` can include `citekey` if passed in `raw_dict`, but the value should be deterministic code-derived metadata, not LLM output.
  - If the optional vault-relative mode is implemented, derive the path relative to `vault_root` or `output_dir` consistently after mirroring rules are applied.
- `archivatorium/models/metadata.py`
  - Do not add `citekey` to the LLM extraction schema unless the schema is also used as the final rendered metadata schema. Prefer adding it after extraction to avoid LLM-generated citekeys.
- `tests/unit/test_citations.py`
  - Existing expectations assert archive-code-derived `@misc{NPG-SG-N-68-1,...}`; update them to assert filename/path-derived `citekey`.
- `tests/integration/test_metadata_citations.py`
  - Existing test only asserts the archive code appears somewhere in citations; add assertions for frontmatter/table/citekey consistency.
- `archivatorium/services/interlinking_service.py`
  - No required change for citation key generation. Its `bibtex_map` name is misleading because it currently means archive-code-safe fuzzy lookup, not frontmatter `citekey`; consider renaming later to avoid confusion.

### 8. `metadata --dry-run` still writes files

Evidence:

- CLI metadata skips vault template initialization when `dry_run` is set.
- The same function still calls `processor.process_file()` and `mirror_file()`.
- `MetadataProcessor.process_file()` writes `output_file.write_text(...)`; `mirror_file()` creates hardlinks/copies.

Impact:

- `--dry-run` is misleading and can mutate/create a vault.

Recommendation:

- Add a `dry_run` flag to `MetadataProcessor` or gate all write/mirror operations in the CLI.
- Add an integration test asserting no output files are created under `--dry-run`.

Note: This matters less for the current production command if `--dry-run` will not be used, but a CLI flag that writes during dry-run is still unsafe.

## Medium priority

### 9. Remove non-flat topic extraction and dead `TopicExtractor`

Evidence:

- `TopicExtractor` remains in `archivatorium/services/topics_service.py`.
- Runtime CLI wiring now creates `TaggingService` when `--hierarchy-file` is provided.
- `TopicExtractor` references are limited to tests/evaluation scripts and historical specs.
- Product decision: non-flat topic extraction should be removed.

Impact:

- Two topic extraction systems make maintenance and test intent harder to reason about.
- Old tests can pass while the active tagging path regresses.

Recommendation:

- Remove `TopicExtractor` and its non-flat/two-step tests from the production test suite.
- Keep only tests for the active flat `TaggingService` path.
- If evaluation scripts still need old comparisons, move that code outside the package runtime path.

### 10. The primary metadata pass reads existing generated metadata back into the next prompt

Evidence:

- `process_file()` reads the full file content before parsing frontmatter.
- `first_chunk = content[:CHUNK_SIZE]` uses the full file, not `original_body`.
- If reprocessing an enriched note, the prompt includes existing YAML frontmatter, metadata callouts, abstract tags, and citation callouts.

Impact:

- Re-runs can reinforce prior outputs instead of extracting from source text.
- Prompt budget is wasted on generated metadata and citations.
- Entity/topic extraction can be biased by previous tags.

Recommendation:

- Build LLM context from cleaned source body, not from the full generated Markdown file.
- Strip known generated callouts (`[!info] Metadata`, `[!abstract]`, `[!citing this document]`) before extraction.
- Preserve or merge legitimate user/frontmatter metadata only outside the LLM prompt path, during deterministic rendering/reconciliation.
- Preserve consistency by rebuilding compact context from generated outputs before processing, then passing only controlled vocabulary hints to the LLM:
  - top conceptual tags from `#Tags/...`
  - top entities grouped by `#Entities/State/...`, `#Entities/Org/...`, `#Entities/City/...`
  - no generated summaries, abstracts, citation blocks, or prior metadata tables
- Reconcile metadata and tags deterministically after both LLM calls:
  - normalize all tags through one canonical parser
  - derive tag counters from canonical tags, not from metadata fields
  - keep document metadata fields (`title`, `summary`, `date`, `archive_code`, etc.) independent of tag extraction
  - if metadata and tags conflict, prefer the authoritative tag model for entity/tag output and record a warning instead of feeding generated output back into the next prompt

Detailed consistency model:

```text
existing generated outputs -> canonical tag parser -> counters/context
source markdown only       -> metadata LLM + tagging LLM
metadata + tags            -> deterministic reconciliation/rendering
rendered output            -> ingest canonical tags for the next file
```

This gives cross-document consistency without contaminating extraction with previously generated summaries, abstracts, citations, or metadata tables.

### 11. Interlink discovery stores only filenames, not vault-relative paths

Evidence:

- `discover()` calculates `filename = md_file.name` and stores that in `code_map` and `bibtex_map`.
- `VaultDocument.vault_relative_path` exists but is not used.
- Links generated by `resolve_link()` are therefore basename links, not relative paths.

Impact:

- Duplicate filenames in different directories become ambiguous.
- Links from nested folders can point incorrectly.

Recommendation:

- Store `md_file.relative_to(self.vault_dir).as_posix()` in maps.
- Generate full vault-relative Markdown links, matching the interlinking specification.

### 12. Tagging service silently returns empty tags on LLM failure

Evidence:

- `_extract_chunk()` catches all exceptions, logs an error, and returns `WindowTaggingResult()`.
- `process_file()` continues and writes output without surfacing that precision tagging failed.

Impact:

- Metadata extraction can appear successful while entities/topics/tags are missing.
- Batch runs hide degraded output quality.

Recommendation:

- Return structured failure information, count failed chunks, and surface warnings in CLI output.
- Consider failing the document when tagging is requested but every tagging chunk fails.

### 13. `index` command does not ensure output directory exists

Evidence:

- CLI calls `service.generate_xlsx(output_dir / "metadata_index.xlsx")`.
- `generate_xlsx()` passes that path directly to `xlsxwriter.Workbook`.
- No `output_dir.mkdir()` occurs in the index command or service.

Impact:

- `archivatorium index vault new-output-dir` can fail if the directory does not already exist.

Recommendation:

- Create `output_path.parent` before opening the workbook.

### 14. Merge interlinking and indexing into one vault-finalization workflow

Evidence:

- The `index` command scans the vault, parses frontmatter, extracts abstract tags, and writes Markdown index pages plus `metadata_index.xlsx`.
- The `interlink` command scans the same vault, parses frontmatter, builds archive-code/language maps, modifies Markdown bodies/tables, and writes files in place.
- Both commands need vault-relative paths, parsed frontmatter, document language, archive codes, references, and generated output parsing.
- `InterlinkingService.discover()` currently stores filenames instead of full vault-relative paths, while `IndexingService` already computes `file_path.relative_to(self.input_dir)`.
- Running index before interlink can index stale generated output if derived references/language versions are expected to exist in rendered tables.
- Generated index pages are Markdown files in the vault and can be accidentally scanned on later runs unless the postprocessing pipeline explicitly excludes generated index files.

Impact:

- Two separate vault scans duplicate IO and parsing logic.
- Frontmatter parsing, vault-relative path handling, and generated tag parsing can drift between services.
- Users need to remember the correct postprocessing order.
- Re-runs can accidentally index generated index pages or interlink generated index pages if those files are not excluded.

Recommendation:

- Merge the user-facing postprocessing workflow into one `interlink VAULT_DIR` command/stage that runs after metadata generation.
- The command must operate only on the generated output vault directory. It must not require the source input directory or a separate output directory.
- Keep internal responsibilities separate:
  - `VaultCorpus` or equivalent shared scan: parse vault Markdown once into document records.
  - Interlink stage: resolve archive-code references, enrich Metadata tables, and write changed document files.
  - Index/XLSX stage: consume the same corpus/canonical tag model and write index pages plus `metadata_index.xlsx` into the same vault.
- Run interlinking before index/XLSX generation.
- After interlink writes document changes, either update the in-memory corpus or reparse only the changed documents before generating outputs.
- Exclude generated output files from the corpus scan, including `Index - *.md`, `metadata_index.xlsx`, template files, and other known generated non-document files.
- All operations inside `interlink` must be idempotent: repeated calls on the same vault with the same options must leave document files, Metadata tables, index pages, and `metadata_index.xlsx` in the same state.
- Interlinking idempotency means existing links are replaced or normalized, never nested or duplicated; `language_versions` has at most one current row; `references` are deduplicated and sorted by the deterministic rule.
- Index/XLSX idempotency means generated index pages and `metadata_index.xlsx` are overwritten deterministically, not appended to, and are excluded from the next scan.
- Keep dry-run semantics stage-aware:
  - interlink dry-run reports document mutations without writing
  - index dry-run reports generated index/XLSX outputs without writing
- Preserve ability to call internal stages independently from tests, but make the production CLI expose `interlink` as the normal postprocessing path.

## Lower priority / cleanup

### 15. `MetadataProcessor.process_file()` is too large and mixes unrelated concerns

Evidence:

- Ruff reports `process_file()` has 49 branches and 159 statements.
- The method handles reading, prompting, fallback extraction, frontmatter normalization, callout assembly, original-body cleanup, citation generation, and writing.

Impact:

- Behavioural changes are risky because unrelated paths are coupled.
- Targeted tests are harder to write.

Recommendation:

- Extract focused helpers: build primary prompt, extract primary metadata, build tagging sections, clean original body, render output document, write output.
- Make `process_file()` an explicit internal pipeline:

```text
read_source
parse_source_and_strip_generated_sections
extract_document_metadata
extract_generated_tags
reconcile_metadata_and_tags
render_frontmatter
render_callouts
write_output
ingest_generated_output_tags
```

- Keep each stage small enough to test independently.

### 16. Centralize generated tag parsing and normalization

Evidence:

- `prefix_tag()`, `normalize_tag_component()`, `TaggingService.extract_tags()`, `IndexingService._parse_entity()`, and resume/index/XLSX logic all need to understand tag structure.
- Current parsing is spread across services and still mixes old unprefixed tags with generated root-prefixed tags.

Impact:

- The same tag can be normalized differently in different subsystems.
- Resume, indexing, XLSX, and rendering can drift.
- It is harder to make `#Entities/...`, `#Topics/...`, and `#Tags/...` authoritative if each subsystem parses them separately.

Recommendation:

- Add one canonical parser/normalizer for generated tags, e.g. `archivatorium.utils.tags`.
- It should parse generated Markdown into a structured model:

```python
{
    "conceptual": ["NATO", "Nuclear-Planning"],
    "entities": {
        "State": ["France"],
        "Org": ["NATO"],
        "City": ["France/Paris"],
        "Person": []
    },
    "topics": ["Category/Doctrine/Nuclear-Deterrence"]
}
```

- Use this parser for:
  - resume counter rebuilding
  - generated-output ingestion after each processed file
  - indexing
  - XLSX export
  - tests for rendered output
- Keep `prefix_tag()` as a rendering helper, not as the only source of tag semantics.

### 17. Cache static tagging prompt material

Evidence:

- `TaggingService._generate_tagging_prompt()` dumps taxonomy YAML and joins useful tags for every chunk.
- Sliding-window documents repeat that work per window.

Impact:

- Avoidable CPU/string work on large batches.
- More noise in the hot path around LLM calls.

Recommendation:

- Precompute taxonomy prompt text and useful-tags prompt text in `TaggingService.__init__()`.
- Reuse the pre-rendered strings for every chunk.
- If topic mode is now always flat, precompute the flattened taxonomy once and remove non-flat branching.

### 18. Replace legacy counters with generated-tag counters

Evidence:

- Current counters are `tag_counts`, `state_counts`, `org_counts`, and `city_counts`.
- Entity counters are updated from obsolete `mentioned_*` fields.
- Conceptual tags from the authoritative tagging pass are not currently the main counter source.

Impact:

- Counter context is tied to the fields that should be removed.
- Resume and in-process consistency use different representations.

Recommendation:

- Replace legacy counters with:

```python
conceptual_tag_counts: Counter[str]
entity_counts: dict[str, Counter[str]]  # State, Org, City, Person
topic_counts: Counter[str]
```

- Populate them only from canonical generated tags.
- Update counters after every rendered output and during resume preflight.

### 19. Prompt/schema naming still carries legacy spelling and terminology

Evidence:

- Code uses `mentioned_organisations` while some specs mention `mentioned_organizations`.
- Older docs/specs still mention `transaction`, `correspondence`, and `mentioned_*` fields.

Impact:

- Confusing for users and future maintainers.
- Increases chance of schema/export mismatch.

Recommendation:

- Decide canonical spelling and field names.
- Remove old names from production schemas and prompts; do not add migration aliases unless a separate archival migration feature is explicitly requested later.

### 20. Lint baseline is noisy

Evidence:

- `ruff check archivatorium tests` reports 63 issues, mostly complexity and line length, plus a few concrete style issues such as unsorted imports and unused imports.

Impact:

- Real lint signals are harder to spot.

Recommendation:

- Either fix the low-effort issues now or configure ignores for accepted complexity in Click commands/tests.
- Keep the active source tree lint-clean enough that future regressions stand out.

## Suggested implementation order

1. Fix the production correctness bugs: generated tag/entity indexing, XLSX pivot, resume counter rebuilding, and full vault-relative interlink paths.
2. Specialize CLI defaults so the standard production command does not require `--pdf-dir`, `--vault-root`, or `--flat-topics`, while still requiring explicit `--hierarchy-file` and `--tags-file`.
3. Replace the primary metadata schema/prompt so the normal path stops extracting unused `mentioned_*` fields and legacy flat tags.
4. Add the canonical generated-tag parser and use it for resume, indexing, XLSX, and output ingestion.
5. Generate deterministic filename-derived `citekey` values and make frontmatter, Metadata table, and BibTeX citations consume the same key.
6. Define and test the frontmatter/Metadata table consistency contract.
7. Merge interlinking and indexing into one vault-finalization workflow with a shared vault scan.
8. Strip generated metadata/callouts from LLM context during reprocessing while passing only compact counter-derived vocabulary hints.
9. Replace legacy counters with generated conceptual/entity/topic counters.
10. Cache static tagging prompt material.
11. Remove `TopicExtractor` and non-flat topic mode from the production code path.
12. Refactor `MetadataProcessor.process_file()` into a pipeline after behaviour is covered by tests.
13. Fix lower-use CLI traps (`--mask`, `--dry-run`) if those flags remain exposed.

## Spec Kit Drafts

Use these as abstract `/speckit.specify` inputs. They are merged into four coherent features so the work is broad enough for Spec Kit but still has clear boundaries.

When these drafts are converted into Spec Kit features, treat them as an update to the existing metadata/tagging/indexing/interlinking line of specs, not as a replacement for unrelated OCR/DOCX features. Existing behaviour from compatible specs should be preserved unless the draft explicitly supersedes it.

### 1. Canonical Generated Tag Data Layer

```text
Create a canonical generated tag data layer for generated OCRPolish Markdown.

The system must treat #Entities/..., #Topics/..., and #Tags/... as the authoritative tag syntax. It must parse generated Markdown into a structured model containing conceptual tags, grouped entities, and topics. The parser must normalize tags consistently and deduplicate values.

The canonical parsed model must store normalized tag paths without the leading #. Rendering helpers may add # when writing Markdown. The parser should retain enough information to render canonical tags again, but counters, indexing, XLSX, and resume logic should consume the normalized structured model rather than raw Markdown strings.

The parser must support entity types State, Org, City, and Person. City tags use the form #Entities/City/<State>/<City>. Topic tags use #Topics/<taxonomy-path>, and conceptual tags use #Tags/<tag>. Malformed generated tags must be ignored with a warning or reported as parse diagnostics; they must not update counters silently.

The parser must ignore obsolete unprefixed tags. Legacy tag support is not needed and must not be implemented in the production parser.

The system must replace legacy metadata counters with counters derived only from canonical generated tags. Counters must include conceptual tags, topics, and entities grouped by entity type. Counter storage and update logic must be independent of frontmatter metadata schema fields.
```

### 2. Resume-Safe Source-Only Metadata Processing

```text
Make metadata processing resume-safe and prevent generated metadata from being fed back into LLM prompts.

Before processing new files, the system must scan already generated Markdown outputs in the output directory exactly once, parse their authoritative generated tags with the canonical tag parser, and rebuild conceptual tag, entity, and topic counters. When a file is skipped because its output already exists and overwrite is false, the skipped output must contribute to counters only if it was not already included in the preflight scan.

When extracting metadata or tags, the system must use only cleaned source Markdown content. If the input file is already enriched, the system must strip generated frontmatter, Metadata callouts, Abstract callouts, citation callouts, and other generated sections before building LLM prompts.

Cross-document consistency must come from compact vocabulary hints derived from canonical counters. It must not come from generated summaries, abstracts, citation blocks, metadata tables, or old frontmatter fields.

The production metadata LLM schema must exclude obsolete mentioned_states, mentioned_organisations, mentioned_cities, and legacy tags fields. Entity, topic, and conceptual tag extraction must be handled only by the tagging path that produces #Entities/..., #Topics/..., and #Tags/....

The production metadata model must keep only document metadata needed for frontmatter, the Metadata table, the Abstract callout, and citations. Canonical frontmatter/table fields are title, summary, pages, source, sender, recipient, intent, author_name, author_institution, date, archive_code, citekey, language, location_city, location_state, and references. The summary field must be exactly one sentence, matching the current code-level schema and prompt. Abstract text is rendered in the Abstract callout rather than as a frontmatter/table field. Raw references are canonical document metadata stored as archive-code strings; rendered reference links may be enriched by deterministic interlinking in the Metadata table without mutating YAML frontmatter.

The citekey field must be deterministic code-derived metadata, not LLM output. By default it must be generated from the output filename stem. An optional mode may generate it from the full vault-relative output path without the .md suffix to avoid collisions across folders. In both modes the final key must be normalized with safe BibTeX characters and stored in frontmatter, rendered in the Metadata table, and used as the BibTeX @misc citekey. The archive_code remains archival metadata and must not be used as the BibTeX citekey.

YAML frontmatter and the rendered Metadata table/callout must be generated from the same reconciled metadata model. They must semantically agree for canonical document metadata fields. The rendered table may include deterministic derived navigation fields, such as interlinking-derived references or language versions, only when those fields are explicitly identified as derived output.

Legitimate user-supplied frontmatter may be preserved only through deterministic reconciliation after source extraction. Generated output sections must be stripped before LLM prompting. If user-supplied metadata conflicts with newly extracted metadata, the reconciliation rule must be explicit per field before implementation; no generated frontmatter or generated callout content may be used as LLM context.
```

### 3. Vault Finalization, Generated Tag Indexing, And XLSX Export

```text
Create one idempotent `interlink VAULT_DIR` vault-finalization workflow that operates only on the generated output vault. It must interlink generated documents and produce Markdown index pages plus XLSX export from the canonical generated tag model.

The workflow must scan the generated vault once into shared document records containing vault-relative path, frontmatter metadata, source body, archive_code, language, raw references, generated tags, entities, and topics.

Interlinking must run before index and XLSX generation. It must resolve archive-code references using full vault-relative Markdown paths, enrich Metadata table references, add language_versions when appropriate, and preserve YAML frontmatter. It must not mutate generated tags.

If interlinking changes document files, the workflow must update the in-memory document records or reparse changed documents before producing Markdown indices and XLSX output.

Every operation in the interlink workflow must be idempotent. Re-running `interlink VAULT_DIR` with the same options must produce the same vault state: links must not be nested, references and language_versions rows must not be duplicated, index pages must be overwritten deterministically, metadata_index.xlsx must be regenerated deterministically, and generated index/XLSX/template files must not be treated as source documents.

Indexing must parse #Entities/..., #Topics/..., and #Tags/... using the canonical tag parser. State, City, Org, Person, Topic, and conceptual tag indices must be generated from these authoritative tags.

Indexing must no longer depend on obsolete unprefixed tags such as #State/... or #Org/... in the normal production path.

XLSX export must pivot away from MetadataSchema.model_fields and obsolete mentioned_* columns. It must export core document metadata plus generated-tag-model columns for State, City, Org, Person, Topic, and conceptual tag values.

Core document metadata exported to XLSX must include citekey so spreadsheet exports, frontmatter, Metadata tables, and BibTeX citations can be reconciled by the same stable citation key.

The production CLI must expose this workflow as `interlink VAULT_DIR`. The command must not require a source input directory or a separate output directory. Markdown index pages and metadata_index.xlsx should be written into VAULT_DIR.

Generated Markdown index pages should cover the authoritative generated model: Index - States.md, Index - Cities.md, Index - Organizations.md, Index - People.md, Index - Topics.md, and Index - Tags.md. States, organizations, people, topics, and conceptual tags should be grouped alphabetically; cities should be grouped by parent state.

The shared scan must exclude generated non-document outputs such as Index - *.md, metadata_index.xlsx, template files, and other known generated vault support files.

The XLSX export must use the same canonical tag parser as indexing and resume counters, so generated indices and spreadsheets reflect the same tag/entity/topic values.
```

### 4. Production Metadata Pipeline Simplification

```text
Simplify the production metadata pipeline and remove obsolete topic modes.

The metadata command must default vault_root to output_dir and pdf_dir to output_dir for compatibility, but generated source links must be derived from the mirrored output layout, not from the input PDF lookup directory. Generated PDFs must always be mirrored into pdf/, and generated source links must point to [[pdf/<filename>.pdf]]. The hierarchy file and tags file must remain explicit required command options.

The intended production command is:
python -m archivatorium.cli metadata NATO_NPG_source NATO_NPG_metadata.v5 --hierarchy-file topics/NATO_themes.yaml --tags-file topics/USEFUL_TAGS.yaml

Non-flat topic extraction must be removed from the production codebase. The old TopicExtractor and two-step/non-flat topic extraction path must be removed from runtime metadata processing and from the production test suite. If old evaluation scripts are still useful, they must live outside the package runtime path and must not define production behaviour. Flat topic extraction must be the only production topic extraction mode. Tests for production behaviour must focus on the flat TaggingService path.

MetadataProcessor.process_file must be refactored into an explicit internal pipeline while preserving observable output behaviour. The pipeline stages should be: read source, parse source and strip generated sections, extract document metadata, extract generated tags, reconcile metadata and tags, render frontmatter, render callouts, write output, and ingest generated output tags. Each stage must expose testable inputs and outputs so regressions can be covered independently.

The tagging service must precompute static taxonomy prompt text and useful tag prompt text during initialization. Since flat topic extraction is the production path, flattened taxonomy should be computed once and reused for every chunk. Sliding-window tagging must not repeatedly dump taxonomy YAML or rebuild static prompt sections per window.

The refactor must preserve existing compatible metadata-output behaviour: mirrored source structure, Obsidian vault initialization, Metadata/Abstract/Citation callout ordering, citation generation, page counting from page headers, and interlinking compatibility.
```

## Verification performed

Focused tests passed:

```text
pytest tests/unit/test_metadata_processor.py tests/unit/test_tag_prefixing_integration.py tests/unit/test_indexing_service.py tests/unit/test_tagging_service.py tests/unit/test_interlinking_service.py tests/integration/test_metadata_command.py tests/integration/test_tagging_pass.py -q
25 passed
```

Static lint was run:

```text
ruff check archivatorium tests
63 issues reported
```
