# Quickstart: Metadata Correctness Fixes

## Prerequisites

- Python environment for the project is installed.
- Test hierarchy and useful-tags fixtures are available through the test suite.
- Run commands from the repository root.

## Focused Validation

### Resume Counters

```bash
pytest tests/integration/test_resume_safety.py tests/unit/test_processor_counters.py
```

Expected outcomes:
- Generated document outputs are counted exactly once.
- Index pages, templates, support files, hidden folders, sidecars, and support artifacts do not affect counters.
- Skipped outputs already scanned by preflight are not double-counted.
- Skipped outputs not scanned by preflight are parsed once.

### Tagging Quality

```bash
pytest tests/unit/test_tagging_service.py tests/unit/test_nlp_normalization.py tests/integration/test_obsidian_metadata.py
```

Expected outcomes:
- Substantive documents require at least three conceptual tags in the initial tagging result.
- Missing, omitted, empty, or undersized conceptual tags fail with an explicit tagging-quality error.
- Administrative stubs may accept empty conceptual tags only after deterministic non-substantive classification.
- Hierarchical conceptual tags such as `#Tags/WINTEX/73` are accepted without malformed-tag warnings and preserve their full path.
- Duplicate suppression preserves justified conceptual archival vocabulary, useful acronyms, exercise names, and preferred-vocabulary paths.

### Canonical Indexing and XLSX Export

```bash
pytest tests/unit/test_indexing_service.py tests/unit/test_xlsx_export.py tests/integration/test_interlink_cli.py
```

Expected outcomes:
- Canonical `#Tags/...`, `#Topics/...`, and `#Entities/...` populate index and XLSX columns.
- Obsolete unprefixed tags do not populate canonical columns.
- Generated index pages do not become resume counter sources.

### Metadata Mask and Dry Run

```bash
pytest tests/integration/test_metadata_command.py tests/integration/test_dry_run.py tests/unit/test_file_exclusion.py
```

Expected outcomes:
- `metadata --mask` enriches only matching Markdown files.
- `.filtered.md` files are not enriched.
- `metadata --dry-run` leaves the filesystem unchanged, including vault templates, generated Markdown, mirrored PDFs, copied or linked files, sidecars, and existing outputs.
- Non-dry-run PDF mirroring places source PDFs under each generated Markdown folder's local `pdf/` directory.

## Full Quality Gates

```bash
ruff check .
ruff format --check .
flake8
mypy .
pytest
coverage run -m pytest
coverage report
```

Expected outcomes:
- All quality gates pass.
- Coverage remains within the project threshold.

Validation completed with 189 passing tests and 94% total coverage. Because
`pytest` already enables `pytest-cov` through project configuration, standalone
coverage validation should be run as `coverage run -m pytest -o addopts=''`
followed by `coverage report`.

## Manual Smoke Scenario

1. Prepare a temporary input directory with two Markdown files, one PDF in a nested source folder, one nonmatching Markdown file, and one `.filtered.md` sidecar.
2. Prepare an output vault containing one generated document page, one `Index - Tags.md`, one template file, and one hidden-folder Markdown file.
3. Run metadata with `--mask` matching only one source Markdown file and `--dry-run`.
4. Confirm no output files changed.
5. Run metadata without `--dry-run`.
6. Confirm only matching Markdown was enriched, resumed counters reflect only eligible generated document pages, hierarchical `#Tags/.../...` values are preserved, and the nested source PDF is mirrored beside the generated Markdown file, for example `.../1973/pdf/NPG-D(73)11_FRE.pdf` with a `[[pdf/NPG-D(73)11_FRE.pdf]]` source link.
