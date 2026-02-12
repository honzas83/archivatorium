# CLI Contract: ocrpolish

The `ocrpolish` command is implemented using Python's `argparse` module.

## Usage

```bash
python -m ocrpolish.cli [OPTIONS] input_dir output_dir
```

## Arguments

- `input_dir`: Path to the directory containing raw OCR markdown files.
- `output_dir`: Path where processed files will be saved.

## Options

- `--mask TEXT`: Glob pattern for files to process (default: `*.md`).
- `--threshold FLOAT`: Frequency threshold (0.0-1.0) for header/footer detection (default: `0.5`).
- `-v, --verbose`: Increase output verbosity.
- `-q, --quiet`: Suppress all but error messages.

## Exit Codes

- `0`: Success.
- `1`: Argument error (missing paths, etc.).
- `2`: Processing error (permission issues, etc.).

## Example

```bash
python -m ocrpolish.cli ./data/raw ./data/cleaned --mask "*.txt" --threshold 0.8
```
