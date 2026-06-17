# Quickstart: Item Type Metadata

## Prerequisites

- Python 3.12 environment with project dependencies installed.
- Ollama metadata extraction available for end-to-end runs.
- Synthetic test inputs only; do not add real archival data to version control.

## Validate With Tests

Run targeted checks for the changed surfaces:

```bash
pytest tests/unit/test_metadata_schema.py tests/unit/test_metadata_processor.py tests/unit/test_xlsx_export.py
```

Expected outcomes:

- `MetadataSchema()` defaults `item_type` to `other`.
- Invalid item-type values are rejected or normalized according to the implementation contract.
- Explanatory/advisory/status documents use `report`.
- Generated metadata ordering places `item_type` first.
- Metadata prompt guidance lists the approved vocabulary and adjacent-type rules before the title, summary, and other field instructions.
- XLSX export includes an `Item Type` column with the generated value.

## Validate Generated Metadata

Create a temporary input directory with simple synthetic Markdown files:

```text
tmp-input/
├── letter.md          # letter/cable style content
├── report.md          # report style content
├── agenda.md          # agenda list content
└── unclear.md         # fragmentary or unsupported form
```

Run metadata generation using the normal CLI workflow:

```bash
ocrpolish metadata tmp-input tmp-vault --overwrite
```

Expected outcomes:

- Each generated Markdown file begins frontmatter with `item_type`.
- `letter.md` uses `correspondence` when the communication form is clear.
- `report.md` uses `report` when the report form is clear.
- `agenda.md` uses `agenda` when the planned order of business is clear.
- `unclear.md` uses `other` when no approved type is clearly supported.
- Existing metadata fields follow `item_type` in their prior relative order.

## Validate Export Surface

Generate or refresh the vault index:

```bash
ocrpolish finalize tmp-vault
```

Expected outcomes:

- `tmp-vault/metadata_index.xlsx` contains an `Item Type` column.
- Rows for newly generated files contain only approved `item_type` values.
- Historical rows without the field remain readable and do not receive unapproved labels during export.

## Full Quality Gates

Before implementation is considered complete, run the project quality gates required by the constitution:

```bash
ruff check .
ruff format .
flake8
mypy .
pytest
coverage run -m pytest
coverage report
```
