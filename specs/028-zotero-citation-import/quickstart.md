# Quickstart & Validation Guide

## Setup
No special files required. Just standard input files for the `metadata` command.

## Execution
Run the metadata command on your documents:
```bash
ocrpolish metadata data/input data/output --hierarchy-file ...
```

## Expected Outcomes
- The command should complete successfully.
- Inspect the generated output markdown files in `data/output`. The Citation callout section should include an invisible `<span class="Z3988">` containing the document's metadata encoded as a COinS ContextObject.
- You can use a Zotero browser extension when the markdown is rendered as HTML to instantly import the document metadata.
