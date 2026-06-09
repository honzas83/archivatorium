# Contract: Metadata Command

## Command

```bash
python -m ocrpolish.cli metadata INPUT_DIR OUTPUT_DIR --hierarchy-file HIERARCHY_FILE --tags-file TAGS_FILE [OPTIONS]
```

## Required Arguments

- `INPUT_DIR`: Existing source directory. The command recursively processes Markdown files and mirrors non-Markdown files.
- `OUTPUT_DIR`: Output directory and default generated Obsidian vault root.
- `--hierarchy-file HIERARCHY_FILE`: Required taxonomy YAML file for flat topic extraction.
- `--tags-file TAGS_FILE`: Required useful tags YAML file for conceptual tag reuse.

## Optional Arguments

- `--mask MASK`: Markdown glob, default `*.md`.
- `--model MODEL`: Ollama model name.
- `--pdf-dir PDF_DIR`: Optional source PDF lookup directory. If omitted, defaults to `OUTPUT_DIR` for compatibility.
- `--vault-root VAULT_ROOT`: Optional Obsidian vault root. If omitted, defaults to `OUTPUT_DIR`.
- `--citekey-mode {stem,path}`: Existing deterministic citekey mode.
- `--overwrite`: Reprocess existing Markdown output.
- `--dry-run`: Run without writing output files.

## Removed/Unavailable Production Options

- No production option may select non-flat topic extraction.
- The old `--flat-topics` mode switch must not be required for flat production behaviour; flat extraction is the only production mode.

## Output Contract

- Markdown output preserves the input directory structure under `OUTPUT_DIR`.
- Source PDFs are mirrored into a `pdf/` directory in the generated vault layout.
- Generated Markdown frontmatter `source` values point to the mirrored PDF with `[[pdf/<filename>.pdf]]`.
- Generated source links never expose the input PDF lookup directory.
- Obsidian vault initialization remains compatible with existing template initialization.
- Generated content preserves frontmatter, Metadata callout, Abstract callout, original body, and Citation callout compatibility.

## Failure Contract

- Missing `--hierarchy-file` fails before processing and names the missing option.
- Missing `--tags-file` fails before processing and names the missing option.
- Missing or invalid input paths fail before processing.
- PDF mirror collisions must either be resolved deterministically or reported before an ambiguous `source` link is written.
