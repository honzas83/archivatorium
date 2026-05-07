# Quickstart: Obsidian Presentation Enhancement

## Overview
This feature automates the setup of an Obsidian vault and enhances the visual presentation of document metadata.

## Setup
No additional configuration is required. The feature is integrated into the `metadata` command.

## Usage
Run the metadata extraction as usual:

```bash
ocrpolish metadata ./input ./output --model gemma4:26b
```

### Automatic Vault Initialization
The first time you run `metadata` on an output directory, `ocrpolish` will:
1. Create a `.obsidian/` folder in the output directory.
2. Copy `app.json` and `appearance.json` from the reference folder to configure the vault (e.g., hiding frontmatter properties).
3. Copy `CONTENT.base` to the vault root.

### Enhanced Metadata View
Each generated markdown file now starts with a formatted metadata table inside an `[!info] Metadata` callout. This ensures metadata is visible even when Obsidian's native property view is hidden.

### Normalized Citations
Direct citations within topic reasons are automatically normalized to italicized double quotes:
- *Before*: `Topic — according to 'Document X'...`
- *After*: `Topic — according to _"Document X"_...`

### Updated BibTeX
BibTeX citations at the end of documents now use the modern `date` field:
```bibtex
@misc{citekey,
  author = {...},
  title = {...},
  date = {1973-10-05},
  ...
}
```
