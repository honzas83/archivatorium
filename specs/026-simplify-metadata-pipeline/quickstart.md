# Quickstart: Simplify Metadata Pipeline

## Prerequisites

- Python environment with project dependencies installed.
- Ollama test calls mocked for automated tests, or a local model available for manual smoke runs.
- Temporary input/output directories. Do not commit real production data.

## Validate CLI contract

Run the production command shape against a temporary fixture containing one Markdown file and matching PDF:

```bash
python -m ocrpolish.cli metadata NATO_NPG_source NATO_NPG_metadata.v5 --hierarchy-file topics/NATO_themes.yaml --tags-file topics/USEFUL_TAGS.yaml
```

Expected outcomes:
- Command does not require `--vault-root`, `--pdf-dir`, or a topic-mode flag.
- Output Markdown is created under the mirrored source structure.
- The source PDF is mirrored under `pdf/` in the generated vault layout.
- Generated frontmatter contains `source: [[pdf/<filename>.pdf]]`.

## Validate required options

Run without hierarchy file:

```bash
python -m ocrpolish.cli metadata NATO_NPG_source NATO_NPG_metadata.v5 --tags-file topics/USEFUL_TAGS.yaml
```

Expected outcome: command fails before processing and reports the missing hierarchy file option.

Run without tags file:

```bash
python -m ocrpolish.cli metadata NATO_NPG_source NATO_NPG_metadata.v5 --hierarchy-file topics/NATO_themes.yaml
```

Expected outcome: command fails before processing and reports the missing tags file option.

## Validate flat-only production tagging

Run the production test subset after removing non-flat production paths:

```bash
pytest tests/unit/test_tagging_service.py tests/integration/test_flat_extraction.py
```

Expected outcomes:
- Tests exercise the flat `TaggingService` production path.
- No production test imports or asserts the legacy two-step `TopicExtractor` behaviour.

## Validate staged processing behaviour

Run focused metadata processor tests:

```bash
pytest tests/unit/test_metadata_processor.py tests/unit/test_metadata_stripping.py tests/unit/test_reconciliation.py tests/unit/test_processor_counters.py
```

Expected outcomes:
- Each stage can be tested with controlled inputs and outputs.
- Full-file processing preserves compatible frontmatter, Metadata/Abstract/Citation callout order, page counts, citations, and tag counter ingestion.

## Validate prompt precomputation

Run tagging service tests that process a document requiring multiple windows:

```bash
pytest tests/unit/test_tagging_service.py
```

Expected outcomes:
- Flattened taxonomy and static prompt text are computed once per tagging service instance.
- Sliding-window prompts reuse static taxonomy and useful-tag text for every window.

## Run quality gates

```bash
ruff check .
ruff format --check .
flake8
mypy .
pytest
coverage run -m pytest
coverage report
```

Expected outcome: all gates pass before the feature is considered complete.
