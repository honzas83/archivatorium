# Contract: Metadata Correctness Behaviour

## Existing Commands

This feature changes correctness guarantees for existing commands only:

- `python -m ocrpolish.cli metadata INPUT_DIR OUTPUT_DIR --hierarchy-file TOPICS_YAML --tags-file USEFUL_TAGS_YAML [options]`
- `python -m ocrpolish.cli index INPUT_DIR OUTPUT_DIR [options]`
- `python -m ocrpolish.cli interlink VAULT_DIR [options]`

No new metadata, tag, or finalization command is introduced.

## Metadata Resume Contract

When metadata processing starts or resumes:

- The resume preflight scan must read eligible generated document Markdown outputs only.
- Eligibility must match the generated-document rules used by interlinking/finalization discovery.
- Excluded files include index pages, landing/support `index.md` files, templates, hidden/system folders, sidecars, metadata spreadsheets, and known vault support files.
- Canonical tags from excluded files must not enter resume counters.
- Skipped existing outputs must contribute exactly once.
- A skipped output already scanned during preflight is not reparsed into counters.
- A skipped output not scanned during preflight is parsed once and registered.

## Tagging Contract

For each enriched Markdown source:

- Generated summaries, abstracts, metadata tables, citation blocks, old frontmatter tags, and legacy mentioned fields are excluded from LLM prompt source text.
- The initial tagging request extracts topics, entities, and conceptual tags together.
- Conceptual tag requirements are visible in the prompt and structured output schema.
- For substantive documents, the initial tagging result must include at least three conceptual tags.
- Conceptual tags may be hierarchical canonical paths under `#Tags/...`, including values such as `#Tags/WINTEX/73`.
- Hierarchical conceptual tag paths must be parsed, counted, rendered, indexed, and exported with the full path preserved.
- Empty conceptual tags are accepted only for deterministically non-substantive administrative stubs.
- Omitted, empty, or undersized conceptual tags for substantive documents fail with an explicit tagging-quality error.
- There is no conceptual-tag repair phase.

## Reuse Hint Contract

Resume counters may influence later tagging only as compact hints:

- Conceptual counters are preferred vocabulary for `#Tags/...`.
- Entity counters are preferred vocabulary for `#Entities/...`.
- Topic counters are subordinate hints and cannot override the taxonomy.
- Static useful-tags vocabulary remains preferred conceptual vocabulary.
- New conceptual tags remain allowed when clearly justified by source text.
- Duplicate suppression may remove exact entity/topic duplicates but must remain generic and vocabulary-driven, without hardcoded domain-term preservation lists.

## Index and XLSX Contract

Production indexing and spreadsheet export:

- Populate canonical columns only from canonical parsed tags.
- Do not import, migrate, or reinterpret obsolete unprefixed tags.
- May ignore or report obsolete tags.
- Preserve canonical output for valid `#Tags/...`, `#Topics/...`, and `#Entities/...`.

## PDF Mirroring Contract

When metadata processing mirrors source PDFs:

- Each PDF is mirrored into a `pdf/` subdirectory beside the generated Markdown output for the same source-relative folder.
- The command must not use a single output-root `pdf/` directory for all generated PDFs.
- A generated document at `NPG - Nuclear Planning Group/1 NPG - Nuclear Planning Group/1973/NPG-D(73)11_FRE.md` links to `NPG - Nuclear Planning Group/1 NPG - Nuclear Planning Group/1973/pdf/NPG-D(73)11_FRE.pdf`.
- Generated Markdown source links remain relative, such as `[[pdf/NPG-D(73)11_FRE.pdf]]`.
- Dry-run must not create, copy, or hardlink PDFs.

## Mask and Dry-Run Contract

When `metadata --mask` is used:

- Only matching Markdown files may be sent to metadata enrichment or tagging enrichment.
- `.filtered.md` sidecars are never enriched.
- Nonmatching Markdown files may be mirrored only when mirroring remains intentional and dry-run is false.

When `metadata --dry-run` is used:

- No vault templates are initialized.
- No generated Markdown is written.
- No PDFs are mirrored.
- No non-Markdown files are copied or hardlinked.
- No sidecars or existing output files are created or updated.
- The command may scan inputs, compute planned output paths, and report planned actions.
