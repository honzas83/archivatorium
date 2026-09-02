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

Malformed v2 policy, category, topic, sample, or path data must fail here rather than silently
producing an empty taxonomy.

## Run focused automated tests

```console
pytest tests/unit/test_flattening.py \
  tests/unit/test_nato_taxonomy_v2.py \
  tests/unit/test_tagging_service.py \
  tests/integration/test_tagging_pass.py
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
ruff format --check .
flake8 archivatorium tests
mypy .
pytest
coverage run -m pytest
coverage report
```

Before each implementation commit, inspect `git status --short` and stage only files belonging to
that completed feature task. Existing unrelated modified and untracked files must remain untouched.
