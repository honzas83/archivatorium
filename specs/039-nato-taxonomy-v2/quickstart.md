# Quickstart: NATO Topic Taxonomy V2

## Prerequisites

- Python 3.12 environment with project dependencies installed.
- A configured Ollama model for non-dry-run classification.
- Local validation material under `data/039-nato-taxonomy-v2/`; never add it to Git.

Suggested local layout:

```text
data/039-nato-taxonomy-v2/
├── input/
├── expected/
├── output-v1/
├── output-v2/
└── reports/
```

## Validate the taxonomy without model calls

Create the local input directory, then initialize the metadata command in dry-run mode:

```console
archivatorium metadata data/039-nato-taxonomy-v2/input \
  data/039-nato-taxonomy-v2/output-v2 \
  --hierarchy-file topics/NATO_themes_v2.yaml \
  --tags-file topics/USEFUL_TAGS.yaml \
  --dry-run
```

From a repository checkout where the console script is not installed, use the equivalent entry
point `uv run python -m archivatorium.cli metadata ...`. This form was used successfully during
feature validation.

Malformed v2 policy, category, topic, sample, or path data must fail here rather than silently
producing an empty taxonomy.

## Run focused automated tests

```console
pytest tests/unit/test_flattening.py \
  tests/unit/test_nato_taxonomy_v2.py \
  tests/unit/test_tagging_service.py \
  tests/integration/test_nato_topic_policy.py \
  tests/integration/test_nato_taxonomy_selection.py
```

These tests use synthetic text. They must not import the archive XLSX files or real NATO documents.

## Rerun metadata with v2

Keep prior output intact and run v2 into a separate directory:

```console
archivatorium metadata data/039-nato-taxonomy-v2/input \
  data/039-nato-taxonomy-v2/output-v2 \
  --hierarchy-file topics/NATO_themes_v2.yaml \
  --tags-file topics/USEFUL_TAGS.yaml
```

For a baseline comparison, run v1 separately:

```console
archivatorium metadata data/039-nato-taxonomy-v2/input \
  data/039-nato-taxonomy-v2/output-v1 \
  --hierarchy-file topics/NATO_themes.yaml \
  --tags-file topics/USEFUL_TAGS.yaml
```

The application does not transform old paths. Reprocessing the source documents lets the narrowed v2
definitions decide each topic anew.

## Score the reviewed corpus

Keep expected inclusions/exclusions and reports local. The review must cover:

- all 85 challenged Extended Deterrence and Tactical Nuclear Sharing assignments;
- positive cases for both replacement topics, Nuclear Release Authority, Command Structure and
  Appointments, and NATO Infrastructure and Common Funding;
- consultation, strike-planning, neutrality, intelligence-leak, defense-spending, and Warsaw Pact
  failure patterns;
- administrative-only documents expected to have no thematic topic.

Record overall inclusion/omission accuracy, challenged-case correction rate, positive-topic recall,
and administrative empty-topic rate in an untracked report under
`data/039-nato-taxonomy-v2/reports/`.

Do not infer these model-quality percentages from the earlier XLSX judgments alone. A numeric score
requires a reviewed manifest that maps source documents to expected v2 inclusions and exclusions.

## Preserve v1

After implementation, verify the original taxonomy has not changed:

```console
git diff --exit-code -- topics/NATO_themes.yaml
```

The taxonomy-focused automated test should also assert the expected v1 checksum captured before the
feature is implemented.

## Run all quality gates

```console
ruff check .
ruff format --check archivatorium tests
flake8 archivatorium tests
mypy .
pytest
coverage run -m pytest
coverage report
```

The repository currently invokes these tools through `uv run` when they are not installed globally.
Before each implementation commit, inspect `git status --short` and stage only files belonging to
that completed feature task. Existing unrelated modified and untracked files must remain untouched.

## Validation results

The implementation was validated on 2026-09-02 with the following results:

- `ruff format --check archivatorium tests`: 96 files already formatted.
- Ruff checks for every feature-touched Python file: passed.
- Repository-wide `ruff check .`: 95 existing findings remain outside the feature scope; no
  unrelated files were changed to address this baseline.
- `flake8 archivatorium tests` with the cognitive-complexity plugin: passed.
- `mypy .` with the project installed plus `types-PyYAML` and `openpyxl-stubs`: passed for 97
  source files.
- `pytest`: 354 tests and 3 subtests passed, with 3 warnings.
- `coverage run -m pytest` followed by `coverage report`: 95% total coverage when tests are
  included; the application-only pytest-cov report was 90%.

`openpyxl` is imported by existing tests but is not declared in the project dependencies, so the
full test and coverage commands used `uv run --with openpyxl`. This is an existing test-environment
limitation rather than a runtime dependency introduced by this feature.
