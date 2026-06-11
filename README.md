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

The toolkit provides several primary commands for processing documents: `ocr`, `clean`, `metadata`, `interlink`, and `index`.

### 1. OCR Processing (Ollama VLM)
Converts multipage PDF files in `INPUT_DIR` recursively to Markdown files in `OUTPUT_DIR` using a local VLM (Ollama). Includes on-the-fly rendering and incremental per-page recovery/resumption.

```bash
ocrpolish ocr [OPTIONS] INPUT_DIR OUTPUT_DIR
```

#### Options
- `--host TEXT`: URL for the Ollama server (or environment variable `OLLAMA_HOST`).
- `--user TEXT`: DigestAuth username (or environment variable `OLLAMA_USER`).
- `--password TEXT`: DigestAuth password (or environment variable `OLLAMA_PASSWORD`).
- `--model TEXT`: The VLM model name to use (default: `qwen3.5:9b`).
- `--dpi INTEGER`: DPI for page rendering (default: `300`).
- `--no-page-header`: Do not include `---\n\n# Page N\n\n` markers in the output (Note: this disables page-level resuming).

*Note: Requires system package `poppler` (e.g. `brew install poppler` on macOS or `apt-get install poppler-utils` on Linux).*

### 2. Cleaning OCR Text
Removes headers/footers and reformats paragraphs.

```bash
ocrpolish clean [OPTIONS] INPUT_DIR OUTPUT_DIR
```

#### Options
- `--mask TEXT`: Glob pattern for files to process (default: `*.md`).
- `--width INTEGER`: Typewriter width for wrapping (default: `80`).
- `--dry-run`: Identify boilerplate without writing primary output files.
- `--no-filtered`: Disable generation of `.filtered.md` sidecar files.
- `--frequency-file PATH`: Path for the consolidated frequency report within `OUTPUT_DIR` (default: `frequency.txt`).
- `--docx PATH`: Generate DOCX files alongside Markdown files.
- `--filter-file PATH`: Path to a text file containing phrases to filter out.

### 3. Extracting Metadata
Extracts structured data and flat production topics using a local LLM.

```bash
ocrpolish metadata INPUT_DIR OUTPUT_DIR --hierarchy-file topics/NATO_themes.yaml --tags-file topics/USEFUL_TAGS.yaml [OPTIONS]
```

#### Options
- `--model TEXT`: The Ollama model to use (default: `gemma4:31b`).
- `--mask TEXT`: Glob pattern for Markdown files to enrich (default: `*.md`). Non-matching Markdown files are not sent to metadata or tagging enrichment.
- `--overwrite`: Overwrite existing files in output directory.
- `--hierarchy-file`: Required path to a YAML topic hierarchy (e.g., `topics/NATO_themes.yaml`).
- `--tags-file`: Required path to a YAML file containing useful tags (e.g., `topics/USEFUL_TAGS.yaml`).
- `--vault-root PATH`: Optional Obsidian vault root; defaults to `OUTPUT_DIR`.
- `--pdf-dir PATH`: Optional source PDF lookup directory; defaults to `OUTPUT_DIR`.
- `--citekey-mode {stem,path}`: Deterministic citekey mode.
- `--dry-run`: Scan inputs and report planned metadata actions.

Generated PDFs are mirrored into a `pdf/` folder beside the generated Markdown file, and generated Markdown links to them as `[[pdf/<filename>.pdf]]`.

### 4. Interlinking Obsidian Vault
Post-processes a generated Obsidian vault in-place to cross-link documents using archive codes, generate indices, and export metadata.

```bash
ocrpolish interlink [OPTIONS] VAULT_DIR
```

#### Options
- `--dry-run`: Logs changes without writing.
- `--verbose`: Show detailed matching logs.
- `--force`: Regenerate all links, even if they already exist.
- `--unifications PATH`: Path to custom unification rules YAML.

### 5. Generating Indices
Generates Obsidian index pages and an optional XLSX index from vault metadata.

```bash
ocrpolish index [OPTIONS] INPUT_DIR OUTPUT_DIR
```

#### Options
- `--mask TEXT`: Glob pattern for files to process (default: `*.md`).

## Development

Run quality checks:
```bash
ruff check .
mypy .
pytest
```
