# CLI Command Schema Contract: `archivatorium`

This contract defines the external CLI interface structure for the renamed project `archivatorium`. The command-line tool executes the various pipelines of the toolkit.

## 1. Global Structure

The executable is named `archivatorium`.

```bash
archivatorium [OPTIONS] COMMAND [ARGS]...
```

### Global Options
- `-v, --verbose`: Enable verbose logging.

---

## 2. Subcommands

### `clean`
Post-process OCR Markdown files (wrapping, filtering boilerplate).

```bash
archivatorium clean [OPTIONS] INPUT_DIR OUTPUT_DIR
```

- **Arguments**:
  - `INPUT_DIR` (Path, required): Directory containing input markdown files.
  - `OUTPUT_DIR` (Path, required): Directory where processed files will be written.
- **Options**:
  - `--mask TEXT`: Glob pattern for files to process (default: `*.md`).
  - `--width INTEGER`: Typewriter wrapping width (default: `80`).
  - `--dry-run`: Log actions without modifying files.
  - `--no-filtered`: Disable generation of `.filtered.md` sidecar files.
  - `--frequency-file PATH`: Path for the consolidated frequency report (default: `frequency.txt` inside output dir).
  - `--docx PATH`: Path to generate DOCX files alongside MD.
  - `--filter-file PATH`: Path to text file containing phrases to filter out.

---

### `metadata`
Extract metadata using Ollama and generate sidecar YAML files.

```bash
archivatorium metadata [OPTIONS] INPUT_DIR OUTPUT_DIR
```

- **Arguments**:
  - `INPUT_DIR` (Path, required): Directory containing input files.
  - `OUTPUT_DIR` (Path, required): Directory for mirrored files and metadata sidecars.
- **Options**:
  - `--mask TEXT`: Glob pattern for files to process (default: `*.md`).
  - `--model TEXT`: Ollama model to use (default: `gemma4:31b`).
  - `--pdf-dir PATH`: Directory containing source PDFs.
  - `--vault-root PATH`: Root of the Obsidian vault.
  - `--hierarchy-file PATH` (Required): Path to themes/taxonomy YAML.
  - `--tags-file PATH` (Required): Path to useful tags YAML.
  - `--citekey-mode [stem|path]`: Deterministic citekey generation mode (default: `stem`).
  - `--overwrite`: Overwrite existing output files.
  - `--dry-run`: Log actions without writing files.

---

### `obsidian`
Generate an Obsidian vault from processed Markdown and metadata.

```bash
archivatorium obsidian [OPTIONS] INPUT_DIR OUTPUT_DIR
```

- **Arguments**:
  - `INPUT_DIR` (Path, required)
  - `OUTPUT_DIR` (Path, required)
- **Options**:
  - `--mask TEXT`: Glob pattern (default: `*.md`).
  - `--template-dir PATH` (Required): Template vault directory to clone/copy.

---

### `interlink`
Post-process a generated Obsidian vault in-place to interlink documents, generate indices, and export metadata.

```bash
archivatorium interlink [OPTIONS] VAULT_DIR
```

- **Arguments**:
  - `VAULT_DIR` (Path, required): The directory of the generated Obsidian vault.
- **Options**:
  - `--dry-run`: Log changes without writing.
  - `--verbose`: Show detailed matching logs.
  - `--force`: Force regeneration of links.
  - `--unifications PATH`: Path to custom tag/archive code unification rules.

---

### `ocr`
OCR multipage PDF files using Ollama (VLM) → Markdown.

```bash
archivatorium ocr [OPTIONS] INPUT_DIR OUTPUT_DIR
```

- **Arguments**:
  - `INPUT_DIR` (Path, required): Directory containing PDF files.
  - `OUTPUT_DIR` (Path, required): Output directory for Markdown files.
- **Options**:
  - `--host TEXT`: Ollama server URL.
  - `--user TEXT`: DigestAuth username.
  - `--password TEXT`: DigestAuth password.
  - `--model TEXT`: VLM model to use (default: `qwen3.5:9b`).
  - `--dpi INTEGER`: DPI for page rendering (default: `300`).
  - `--no-page-header`: Do not include "Page X" headers in the output.
