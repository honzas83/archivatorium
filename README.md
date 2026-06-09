# ocrpolish

A specialized toolkit for cleaning, formatting, and validating OCR outputs processed by Large Language Models (LLMs).

## Features

- **Precision Tagging System**: A three-tiered tagging system (Conceptual, Entity, Topic) using flat production topic extraction for high accuracy and signal.

## Obsidian Export Structure

The `metadata` command generates Markdown files with a specific structure designed for Obsidian:

1. **YAML Frontmatter**: Contains core metadata such as `title`, `summary`, `pages`, `intent`, `date`, `archive_code`, and `source` (`[[pdf/<filename>.pdf]]`).
2. **Abstract Callout**: A block containing:
   - The document **title** and **abstract**.
   - **Mentioned Entities**: Hierarchical tags for mentioned states, organizations, and cities (e.g., `State/UK`, `Org/NATO`, `City/UK/London`).
   - **Categories/Topics**: Hierarchical tags extracted from a provided NATO taxonomy.
   - **Tags**: Flat, canonical conceptual keywords (e.g., `#NuclearStrategy`).

### Metadata Prerequisites
The metadata extraction feature requires [Ollama](https://ollama.com/) to be installed and running locally.
```bash
ollama pull gemma4:31b
```

## Usage

The toolkit provides three primary commands: `clean`, `metadata`, and `index`.

### Cleaning OCR Text
Removes headers/footers and reformats paragraphs.

```bash
ocrpolish clean [OPTIONS] INPUT_DIR OUTPUT_DIR
```

#### Options
- `--mask TEXT`: Glob pattern for files to process (default: `*.md`).
- `--width INTEGER`: Typewriter width for wrapping (default: `80`).
- `--dry-run`: Identify boilerplate without writing primary output files.
- `--docx PATH`: Generate DOCX files in the specified directory.

### Extracting Metadata
Extracts structured data and flat production topics using a local LLM.

```bash
python -m ocrpolish.cli metadata INPUT_DIR OUTPUT_DIR --hierarchy-file topics/NATO_themes.yaml --tags-file topics/USEFUL_TAGS.yaml
```

#### Options
- `--model TEXT`: The Ollama model to use (default: `gemma4:31b`).
- `--mask TEXT`: Glob pattern for Markdown files to process (default: `*.md`).
- `--overwrite`: Overwrite existing files in output directory.
- `--hierarchy-file`: Required path to a YAML topic hierarchy (e.g., `topics/NATO_themes.yaml`).
- `--tags-file`: Required path to a YAML file containing useful tags (e.g., `topics/USEFUL_TAGS.yaml`).
- `--vault-root PATH`: Optional Obsidian vault root; defaults to `OUTPUT_DIR`.
- `--pdf-dir PATH`: Optional source PDF lookup directory; defaults to `OUTPUT_DIR`.
- `--citekey-mode {stem,path}`: Deterministic citekey mode.
- `--dry-run`: Skip writes where supported by the command.

Generated PDFs are mirrored into `OUTPUT_DIR/pdf/`, and generated Markdown links
to them as `[[pdf/<filename>.pdf]]`.

### Generating Indices
Generates Obsidian index pages and an optional XLSX index from vault metadata.

```bash
ocrpolish index [OPTIONS] INPUT_DIR
```

#### Options
- `--output-xlsx, -o PATH`: Path to save the XLSX metadata index.
- `--topics-yaml, -t PATH`: Path to the YAML file defining topic hierarchy.
- `--recursive / --no-recursive`: Scan subdirectories (default: `recursive`).


## Development

Run quality checks:
```bash
ruff check .
mypy .
pytest
```
