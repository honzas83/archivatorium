# Quickstart: OCR Post-Processing

## Setup

1. **Environment**:
   Ensure Python 3.12 is installed.
   
2. **Install Quality Tools**:
   ```bash
   pip install ruff flake8 flake8-cognitive-complexity mypy pytest coverage
   ```

## Basic Usage

To clean a directory of OCR files:

```bash
python -m ocrpolish.cli input_docs/ output_docs/
```

## Running Quality Checks

Ensure the project meets the constitution standards:

```bash
ruff check .
flake8 .
mypy .
pytest
```

## Development Workflow

1. Place sample data in `data/` (gitignored).
2. Use the `--mask` option to target specific files.
3. Check the `output/` directory for mirrored structure and cleaned content.
