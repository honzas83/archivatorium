# Quickstart: Metadata Indexing

## Prerequisites
1. An Obsidian vault containing `.md` files processed by `ocrpolish metadata`.
2. A topics YAML file (e.g., `topics/NATO_themes.yaml`).

## Basic Indexing
Generate the standard Markdown index pages in your vault:

```bash
python -m ocrpolish.cli index ./my-vault --topics-yaml topics/NATO_themes.yaml
```

## Exporting to XLSX
Generate both the Markdown indices and a spreadsheet for external analysis:

```bash
python -m ocrpolish.cli index ./my-vault \
    --topics-yaml topics/NATO_themes.yaml \
    --output-xlsx metadata_index.xlsx
```

## Verifying Results
- Open `Index - States.md` in Obsidian and check if #State/ tags are correctly listed.
- Open `metadata_index.xlsx` and verify all expected columns (title, date, summary, etc.) are present and populated.
