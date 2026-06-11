# CLI Contract: OCR Pipeline

## Command

`ocrpolish ocr <input_dir> <output_dir> [OPTIONS]`

## Arguments

- `input_dir` (Directory): Path to the directory containing input PDFs to process.
- `output_dir` (Directory): Path to the target directory where the generated markdown files will be saved, maintaining the input hierarchy.

## Options

- `--host <URL>` (String): URL for the Ollama server (default: `http://localhost:11434` or environment variable `OLLAMA_HOST`).
- `--user <USERNAME>` (String): DigestAuth username (default: environment variable `OLLAMA_USER`).
- `--password <PASSWORD>` (String): DigestAuth password (default: environment variable `OLLAMA_PASSWORD`).
- `--model <MODEL>` (String): The VLM model name to use (default: `qwen3.5:9b`).
- `--dpi <INT>` (Integer): Dots per inch for PDF page rendering (default: 300).
- `--no-page-header` (Flag): If set, do not include `---\n\n# Page N\n\n` markers in the output (Note: this disables resuming functionality for the generated files).

## Environment Variables

- `OLLAMA_HOST`
- `OLLAMA_USER`
- `OLLAMA_PASSWORD`
