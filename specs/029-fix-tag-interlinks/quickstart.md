# Quickstart: Fix Tag and Interlink Bugs

## Prerequisites

- Python 3.12 environment with project dependencies installed.
- Run commands from the repository root.

## Targeted Validation

Run parser, interlinking, and topic-hint tests:

```bash
pytest tests/unit/test_tag_parser.py tests/unit/test_interlinking_service.py tests/unit/test_processor_counters.py tests/unit/test_tagging_service.py
```

Expected outcomes:

- Slash-containing organization and state examples are accepted as dash-normalized raw paths.
- No malformed-generated-tag warning is emitted for the reported organization/state examples.
- Generated document links from nested target paths use only the target filename.
- Topic assignment guidance has no hard maximum.
- Tagging reuse hints include the top 100 topic counter items when at least 100 exist.

## CLI-Level Validation

Run the interlink CLI integration tests:

```bash
pytest tests/integration/test_interlink_cli.py tests/integration/test_tagging_pass.py
```

Expected outcomes:

- Generated metadata callouts keep language labels unchanged.
- References, body, and sibling language-version link destinations are filename-only.
- Existing reference-link behavior remains unchanged.
- Dense substantive documents retain every clearly justified taxonomy topic.

## Full Quality Gates

Before marking implementation complete, run:

```bash
ruff check .
ruff format .
flake8
mypy .
pytest
coverage run -m pytest
coverage report
```

Expected outcomes:

- All commands pass.
- Coverage report includes the updated parser, interlinking, tagging, and counter paths.
