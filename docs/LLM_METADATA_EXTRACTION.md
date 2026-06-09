# LLM Metadata Extraction & Flat Tagging Workflow

This document describes how `ocrpolish` uses Ollama-backed LLM calls to extract
structured document metadata and production tags from OCR-processed Markdown.

## Architectural Overview

`ocrpolish metadata` uses a staged workflow:

1. **Read source**: Load the source Markdown file.
2. **Parse and strip generated sections**: Preserve user frontmatter for
   reconciliation, but remove generated frontmatter/callouts before LLM prompts.
3. **Extract document metadata**: Extract title, summary, abstract, dates,
   actors, archive code, language, location, and references.
4. **Extract generated tags**: Run the flat `TaggingService` path for topics,
   entities, and conceptual tags.
5. **Reconcile metadata and tags**: Combine existing user metadata with newly
   extracted and computed fields.
6. **Render output**: Write YAML frontmatter, Metadata callout, Abstract callout,
   original body, and Citation callout.
7. **Ingest generated tags**: Parse generated output tags back into counters for
   consistency hints across the run.

## Production Command

The production command requires explicit taxonomy and useful-tag files:

```bash
python -m ocrpolish.cli metadata NATO_NPG_source NATO_NPG_metadata.v5 --hierarchy-file topics/NATO_themes.yaml --tags-file topics/USEFUL_TAGS.yaml
```

When omitted, `--vault-root` and `--pdf-dir` default to the output directory for
compatibility. Generated source PDF links are still derived from the generated
vault layout, not from the source PDF lookup directory.

## Primary Metadata Extraction

The metadata pass reads the cleaned source body and asks the LLM for a
`MetadataSchema`. It extracts:

- **Standard identifiers**: title, archive code, language.
- **Temporospatial metadata**: official date, city, state.
- **Narrative metadata**: one-sentence summary and detailed abstract.
- **Correspondence fields**: sender, recipient, and intent.
- **References**: mentioned archive reference codes.

If a large document does not yield a date from the first chunk, the processor
uses a secondary date prompt on the final chunk. Page counts are calculated from
`# Page N` headers.

## Flat Tagging

Production topic extraction is flat-only. The tagging service loads the provided
hierarchy, flattens it once into `Category/Topic` entries, and reuses that static
taxonomy prompt text for every document chunk. Useful tags from
`--tags-file` are normalized once and reused in every prompt.

The tagging pass returns:

- **Entity tags**: `State/<name>`, `Org/<name>`, `City/<state>/<city>`,
  `Person/<name>`.
- **Topic tags**: flat `Category/Topic` tags with quoted evidence in the reason.
- **Conceptual tags**: canonical tags that prioritize the useful-tag vocabulary.

Non-flat and two-step topic extraction are not production modes.

## Obsidian Output

Generated Markdown is organized for Obsidian:

1. **YAML frontmatter**: canonical metadata, including deterministic `source`
   and `citekey`.
2. **Metadata callout**: rendered metadata table.
3. **Abstract callout**: title, abstract, categories/topics, entities, and tags.
4. **Original body**: cleaned source Markdown.
5. **Citation callout**: Chicago-style citation and BibTeX entry.

Generated PDFs are mirrored into the output vault's `pdf/` directory. Source
links in generated Markdown use the stable vault link form:

```text
[[pdf/<filename>.pdf]]
```
