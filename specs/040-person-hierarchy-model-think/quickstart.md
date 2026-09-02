# Quickstart: Hierarchical Person Entities and Model Reasoning Control

## Prerequisites

- Python 3.12 with project dependencies installed.
- An Ollama model for live OCR or metadata runs.
- Synthetic validation inputs under `data/040-person-hierarchy-model-think/` if performing a local
  end-to-end run; do not add real archive data to Git.

## Inspect the CLI contract

```console
uv run archivatorium metadata --help
uv run archivatorium ocr --help
```

Both commands must list `--model-think` with `False`, `low`, `medium`, and `high`, and show `medium`
as the default. Choices are case-insensitive.

An invalid value must fail before processing:

```console
uv run archivatorium ocr data/040-person-hierarchy-model-think/input \
  data/040-person-hierarchy-model-think/output --model-think=maximum
```

## Validate Person paths without live archive data

Run focused synthetic tests:

```console
uv run pytest \
  tests/unit/test_person_entities.py \
  tests/unit/test_tag_parser.py \
  tests/unit/test_tag_validation.py \
  tests/unit/test_tagging_service.py \
  tests/unit/test_indexing_service.py \
  tests/unit/test_markdown_indices.py
```

The cases must prove:

- K-W Andrae and K. W. Andrae normalize to `Entities/Person/Andrae/KW`;
- Joseph Luns becomes `Entities/Person/Luns/Joseph`;
- an unknown given name permits `Entities/Person/Andrae`;
- minister, secretary, ranks, and titles are not added to Person paths;
- invalid depths and missing surnames are rejected;
- parsing, counters, entity output, XLSX export, and People indexing retain the hierarchy;
- People-index alphabetic grouping uses surname, not given name.

## Validate reasoning propagation

Use mocked requests so private reasoning and external model availability do not affect the test:

```console
uv run pytest \
  tests/unit/test_ocr_engine.py \
  tests/unit/test_metadata_processor.py \
  tests/integration/test_cli.py \
  tests/integration/test_metadata_command.py \
  tests/integration/test_ocr_cli.py
```

The tests must cover all four choices, case-insensitive false conversion, medium defaults, invalid
values, conditional date extraction, Qwen 3.8 OCR, and unchanged behavior for other OCR profiles and
tag extraction.

## Optional local rerun

Run metadata into a separate output directory rather than overwriting an earlier archive:

```console
uv run archivatorium metadata \
  data/040-person-hierarchy-model-think/input \
  data/040-person-hierarchy-model-think/output-medium \
  --hierarchy-file topics/NATO_themes_v2.yaml \
  --tags-file topics/USEFUL_TAGS.yaml \
  --model-think=medium
```

For Qwen 3.8 OCR with reasoning disabled:

```console
uv run archivatorium ocr \
  data/040-person-hierarchy-model-think/pdf-input \
  data/040-person-hierarchy-model-think/ocr-output \
  --mode=qwen38 \
  --model-think=False
```

Existing files are not migrated. Rerunning metadata is the supported way to generate the new Person
hierarchy.

## Run all quality gates

```console
uv run ruff check .
uv run ruff format --check .
uv run flake8 archivatorium tests
uv run mypy .
uv run pytest
uv run coverage run -m pytest
uv run coverage report
```

Before every implementation commit, inspect `git status --short` and stage only the files assigned to
the completed feature task. Do not stage existing unrelated test edits or local archive datasets.
