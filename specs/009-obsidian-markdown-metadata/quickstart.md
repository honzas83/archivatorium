# Quickstart: Obsidian Metadata Extraction

This guide shows how to generate Obsidian-compatible metadata for OCR-processed documents.

## Prerequisites
- Ollama running locally.
- `ocrpolish` installed in the virtual environment.

## Usage

To extract metadata from a directory of Markdown files (OCR results) and generate Obsidian-compatible output:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run metadata extraction
python -m ocrpolish.cli metadata <input_directory> <output_directory> --vault-root /path/to/vault
```

The output will be `.md` files in the `<output_directory>` with:
1. Flattened YAML frontmatter.
2. Obsidian-style tags.
3. A `source` property linking to the corresponding `.pdf` using a relative path from the `--vault-root`.

## Example Output

```markdown
---
title: "NATO Council Meeting"
summary: "A meeting to discuss defense planning. It focuses on the 1978 budget."
...
correspondence_sender: "Secretary General"
tags:
  - NATO
  - DefensePlanning
source: "[[Attachments/NPG-D-77-12.pdf]]"
---

[Original OCR content follows...]
```
