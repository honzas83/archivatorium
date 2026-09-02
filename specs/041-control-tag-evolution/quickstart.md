# Quickstart: Controlled Tag Evolution

## Run metadata generation

```bash
archivatorium metadata INPUT_DIR OUTPUT_DIR \
  --hierarchy-file topics/NATO_themes_v2.yaml \
  --tags-file topics/USEFUL_TAGS.yaml \
  --model-think=medium
```

`USEFUL_TAGS.yaml` supplies preferred starting vocabulary but does not prevent the model from adding
a genuinely supported concept. Use `False`, `low`, `medium`, or `high` to control reasoning for both
metadata extraction and every tag-inference request.

## Expected tag behavior

- A substantive document normally receives 5–12 principal conceptual tags, but the model is not
  required to fill a quota.
- Output never contains more than 20 unique conceptual tags or more than five novel tags.
- A new valid tag is retained immediately in its source document.
- It is not offered as preferred vocabulary after only one document.
- Once it appears in two independent archive documents, later documents may reuse it as established
  vocabulary.
- Entity names are excluded from conceptual tags even if they also appear in seed or established
  vocabulary.
- Existing archive documents are not rewritten; rerun metadata with `--overwrite` when regeneration
  is desired.

## Focused verification

```bash
pytest tests/unit/test_tagging_service.py \
  tests/unit/test_tag_suppression.py \
  tests/unit/test_nlp_normalization.py \
  tests/unit/test_processor_counters.py \
  tests/unit/test_metadata_reasoning.py \
  tests/integration/test_model_think_cli.py \
  tests/integration/test_tagging_pass.py \
  tests/integration/test_resume_safety.py
```

Then run the constitutional gates:

```bash
ruff check .
ruff format --check .
flake8 archivatorium tests --max-cognitive-complexity=10
mypy .
pytest
coverage run -m pytest
coverage report
```

Use synthetic fixtures in committed tests. Put any reviewed NATO archive validation material under
gitignored `data/041-control-tag-evolution/`.
