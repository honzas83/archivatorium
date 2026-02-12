# ocrpolish

A specialized toolkit for cleaning, formatting, and validating OCR outputs processed by Large Language Models (LLMs).

## Features

- **Statistical Header/Footer Removal**: Detects and removes repeating boilerplate text across large document sets.
- **Smart Paragraph Merging**: Merges line breaks within paragraphs while protecting Markdown structures (lists, headers, blockquotes).
- **Directory Mirroring**: Replicates the input directory structure in the output directory.
- **2-Pass Processing**: Efficiently handles large datasets by identifying global patterns before transformation.

## Installation

```bash
pip install .
```

For development:
```bash
pip install ruff flake8 mypy pytest coverage
```

## Usage

```bash
python -m ocrpolish.cli [OPTIONS] INPUT_DIR OUTPUT_DIR
```

### Options

- `--mask TEXT`: Glob pattern for files to process (default: `*.md`).
- `--threshold FLOAT`: Frequency threshold (0.0-1.0) for header detection (default: `0.5`).
- `-v, --verbose`: Increase output verbosity.

## Development

Run quality checks:
```bash
ruff check .
mypy .
pytest
```
