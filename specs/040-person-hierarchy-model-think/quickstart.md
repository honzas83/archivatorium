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
uv run archivatorium ocr /tmp /tmp --model-think=maximum
```

## Validate Person paths without live archive data

Run focused synthetic tests:

```console
uv run pytest \
  tests/unit/test_person_entities.py \
  tests/unit/test_person_tagging.py \
  tests/unit/test_tag_parser.py \
  tests/unit/test_tag_validation.py \
  tests/unit/test_indexing_service.py \
  tests/unit/test_markdown_indices.py \
  tests/integration/test_person_entity_hierarchy.py
```

The cases must prove:

- K-W Andrae and K. W. Andrae normalize to `Entities/Person/Andrae/K-W`;
- Joseph M.A.H. Luns normalizes to `Entities/Person/Luns/Joseph-M-A-H`;
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
  tests/integration/test_model_think_cli.py \
  tests/unit/test_ocr_reasoning.py \
  tests/unit/test_metadata_reasoning.py \
  tests/unit/test_ocr_engine.py \
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

## Focused validation result

The synthetic Person suite (38 tests) and reasoning suite (118 tests) passed on 2026-09-02. CLI
help showed all four case-insensitive values with the medium default, and the invalid `maximum`
value was rejected before processing. The optional live Ollama reruns were not required for these
mocked deterministic checks.

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

### Quality-gate result (2026-09-02)

- `ruff format --check archivatorium tests` passed for all 104 files.
- Ruff passed for every feature-created source and test file. The repository-wide `ruff check`
  remains blocked by 83 pre-existing findings in files outside this feature's scope.
- The available system `mypy` could not load the `pydantic.mypy` plugin because it runs outside the
  project virtual environment; the virtual environment does not contain mypy.
- `flake8` is not installed in the project virtual environment or on the host command path.
- The unfiltered pytest run is blocked during collection because the existing
  `tests/unit/test_xlsx_export.py` imports undeclared `openpyxl`, which is not installed.
- Excluding only that environment-blocked test module, all 400 collected tests passed. Coverage was
  90% for `archivatorium/` (95% including tests); both feature utility modules reached 96% or more.
