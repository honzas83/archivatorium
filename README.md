# ocrpolish

A specialized toolkit for cleaning, formatting, and validating OCR outputs processed by Large Language Models (LLMs).

## Features

- **Precision Tagging System**: A three-tiered tagging system (Conceptual, Entity, Topic) using a dynamic two-pass architecture for high accuracy and signal.

## Obsidian Export Structure

The `metadata` command generates Markdown files with a specific structure designed for Obsidian:

1. **YAML Frontmatter**: Contains core metadata such as `title`, `summary`, `pages`, `intent`, `date`, `archive_code`, and `source` (relative link to the PDF).
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
Extracts structured data and hierarchical topics using a local LLM via a two-pass architecture.

```bash
ocrpolish metadata [OPTIONS] INPUT_DIR OUTPUT_DIR
```

#### Options
- `--model TEXT`: The Ollama model to use (default: `gemma4:26b`). Note: Pass 2 tagging defaults to `gemma4:31b` internally.
- `--ollama-url TEXT`: URL of the Ollama server (default: `http://localhost:11434`).
- `--recursive / --no-recursive`: Process subdirectories (default: `recursive`).
- `--overwrite`: Overwrite existing files in output directory.
- `--hierarchy-file, -h`: Path to a YAML topic hierarchy (e.g., `topics/NATO_themes.yaml`).
- `--tags-file, -t`: Path to a YAML file containing useful tags (e.g., `topics/USEFUL_TAGS.yaml`).
- `--vault-root PATH`: Root directory of the Obsidian vault for relative link calculation.
- `--pdf-dir PATH`: Directory containing source PDF files.

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
