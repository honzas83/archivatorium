# ocrpolish

A specialized toolkit for cleaning, formatting, and validating OCR outputs processed by Large Language Models (LLMs).

## Features

- **Metadata Extraction (Ollama)**: Automatically extracts structured metadata (author, date, archive code, etc.) using local LLMs and prepends it as YAML frontmatter.
- **Statistical Header/Footer Removal**: Detects and removes repeating boilerplate text across large document sets.
- **Smart Paragraph Wrapping**: Automatically wraps long lines while preserving lists, tables, and structural markers.
- **Directory Mirroring**: Replicates the input directory structure in the output directory.
- **DOCX Generation**: Converts cleaned Markdown to DOCX with preserved structure.

## Installation

```bash
pip install .
```

### Metadata Prerequisites
The metadata extraction feature requires [Ollama](https://ollama.com/) to be installed and running locally.
```bash
ollama pull gemma4:26b
```

## Usage

The toolkit provides two primary commands: `clean` and `metadata`.

### Cleaning OCR Text
Removes headers/footers and reformats paragraphs.

```bash
ocrpolish clean [OPTIONS] INPUT_DIR OUTPUT_DIR
```

#### Options
- `--mask TEXT`: Glob pattern for files to process (default: `*.md`).
- `--width INTEGER`: Typewriter width for wrapping (default: `80`).
- `--dry-run`: Identify boilerplate without writing primary output files.
- `--docx DOCX_DIR`: Generate DOCX files in the specified directory.

### Extracting Metadata
Extracts structured data and hierarchical topics using a local LLM.

```bash
ocrpolish metadata [OPTIONS] INPUT_DIR OUTPUT_DIR
```

#### Options
- `--model TEXT`: The Ollama model to use (default: `gemma4:26b`).
- `--ollama-url TEXT`: URL of the Ollama server (default: `http://localhost:11434`).
- `--recursive / --no-recursive`: Process subdirectories (default: `recursive`).
- `--overwrite`: Overwrite existing files in output directory.
- `--hierarchy-file, -h`: Optional path to a YAML topic hierarchy (e.g., `topics/NATO_themes.yaml`). If provided, performs a two-step hierarchical topic extraction.
- `--vault-root PATH`: Root directory of the Obsidian vault for relative link calculation.
- `--pdf-dir PATH`: Directory containing source PDF files.

## Development

Run quality checks:
```bash
ruff check .
mypy .
pytest
```
