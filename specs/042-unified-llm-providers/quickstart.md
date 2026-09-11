# Quickstart: Unified LLM Providers

## Prerequisites

- Python 3.12 with project dependencies installed.
- For compatibility validation, an accessible Ollama service and the existing local models used by
  the selected commands.
- For optional e-INFRA validation, an authorized e-INFRA account and API token.
- Only synthetic, non-sensitive validation inputs under `data/042-unified-llm-providers/`.

Do not run remote validation with protected archival material unless its remote processing is
explicitly authorized.

## Protect the local credential

The repository-root `meta-api-key` is a local convenience file, not a project asset. After the
feature adds its root-anchored ignore rule, verify it is ignored and restrict its permissions:

```console
chmod 600 meta-api-key
git check-ignore meta-api-key
```

Prefer a credential stored outside the repository and exposed as `E_INFRA_API_TOKEN`. Never place a
token directly in command arguments, logs, fixtures, committed environment files, or captured test
output.

## Inspect the additive CLI contract

```console
uv run archivatorium metadata --help
uv run archivatorium ocr --help
```

Both commands must show `--llm-provider`, `--llm-base-url`, and `--llm-api-key-file`. Existing
options including `--host`, OCR DigestAuth settings, inference overrides, models, modes, and
reasoning remain present. See [contracts/cli.md](contracts/cli.md) for the complete matrix.

Invalid provider configuration must fail before processing:

```console
uv run archivatorium ocr data/042-unified-llm-providers/pdf-input /tmp/invalid-output \
  --llm-provider e-infra \
  --llm-api-key-file /secure/path/e-infra-token \
  --mode glm
```

Expected outcome: the command identifies the unsupported e-INFRA/GLM combination and creates no
output or model request.

The exact service model list can change. `qwen3.8-27b` is the initial default; an unavailable
explicit or default model fails clearly and is never replaced automatically.

## Validate unchanged Ollama behavior

Run the established commands without any new provider option:

```console
uv run archivatorium metadata \
  data/042-unified-llm-providers/markdown-input \
  data/042-unified-llm-providers/ollama-metadata-output \
  --hierarchy-file topics/NATO_themes_v2.yaml \
  --tags-file topics/USEFUL_TAGS.yaml

uv run archivatorium ocr \
  data/042-unified-llm-providers/pdf-input \
  data/042-unified-llm-providers/ollama-ocr-output \
  --mode qwen38 \
  --model-think medium
```

Expected outcomes:

- Ollama is selected by omission.
- Metadata uses `gemma4:31b`; OCR uses `qwen3.5:9b` unless explicitly overridden.
- Native request shapes, prompts, reasoning, image paths, options, timeouts, retry counts, context,
  traversal, page resume, normalization, and output layout match the compatibility contract.
- Deterministic compatibility fixtures produce byte-identical files. Live model wording may vary
  only because the model itself is nondeterministic.

Run compatibility tests before and after each implementation increment:

```console
uv run pytest \
  tests/integration/test_ollama_compatibility.py \
  tests/unit/test_ollama_provider.py \
  tests/unit/test_ollama_client.py \
  tests/unit/test_ollama_timeout.py \
  tests/unit/test_metadata_reasoning.py \
  tests/unit/test_ocr_engine.py \
  tests/unit/test_ocr_reasoning.py \
  tests/integration/test_metadata_command.py \
  tests/integration/test_model_think_cli.py \
  tests/integration/test_ocr_cli.py
```

The suite must compare complete model request sequences, not only selected fields. See
[contracts/ollama-compatibility.md](contracts/ollama-compatibility.md).

## Validate the shared client without live services

```console
uv run pytest \
  tests/contract/test_llm_client.py \
  tests/unit/test_llm_config.py \
  tests/unit/test_einfra_provider.py \
  tests/integration/test_llm_provider_cli.py
```

Expected coverage includes:

- both provider/default matrices on both commands;
- endpoint alias agreement and conflict;
- credential file/environment precedence, whitespace, permissions, and redaction;
- provider-incompatible option rejection before processing;
- exact Ollama request compatibility;
- e-INFRA Bearer authentication, JSON Schema, Qwen reasoning mapping, image encoding, streaming,
  truncation, error classification, bounded retry, and no fallback;
- metadata, tagging, and OCR depending only on the shared client contract.

## Optional e-INFRA metadata and tagging run

Using the environment credential:

```console
E_INFRA_API_TOKEN="$(< /secure/path/e-infra-token)" \
uv run archivatorium metadata \
  data/042-unified-llm-providers/markdown-input \
  data/042-unified-llm-providers/einfra-metadata-output \
  --llm-provider e-infra \
  --hierarchy-file topics/NATO_themes_v2.yaml \
  --tags-file topics/USEFUL_TAGS.yaml \
  --model-think low
```

Or select the protected file explicitly without placing its value on the command line:

```console
uv run archivatorium metadata \
  data/042-unified-llm-providers/markdown-input \
  data/042-unified-llm-providers/einfra-metadata-output \
  --llm-provider e-infra \
  --llm-api-key-file /secure/path/e-infra-token \
  --model qwen3.8-27b \
  --model-think low \
  --concurrency 4 \
  --hierarchy-file topics/NATO_themes_v2.yaml \
  --tags-file topics/USEFUL_TAGS.yaml
```

Expected outcome: valid existing metadata and canonical-tag output with no provider, usage,
credential, or private-reasoning fields added to the Markdown.

For metadata, `--concurrency` accepts values from 1 through 4 and defaults to 1. Values above one
process independent matching Markdown documents concurrently. Each document retains a sequential
metadata, conditional date, tagging, validation, and persistence chain based on the same completed
preflight vocabulary snapshot. Successful outputs are then reconciled into the global counters and
registry on the coordinator thread. Dry-run does not issue concurrent model requests.

## Optional e-INFRA OCR and resume run

```console
uv run archivatorium ocr \
  data/042-unified-llm-providers/pdf-input \
  data/042-unified-llm-providers/einfra-ocr-output \
  --llm-provider e-infra \
  --llm-api-key-file /secure/path/e-infra-token \
  --model qwen3.8-27b \
  --mode qwen38 \
  --model-think low \
  --concurrency 4
```

Expected outcome: the selected model is verified as multimodal, each page's visible streamed output
is assembled once in order, reasoning is excluded, and existing Markdown page layout is retained.
Interrupt after at least one complete saved run and repeat the command to verify completed pages are
skipped under the existing resume contract.

`--concurrency` accepts values from 1 through 4 and defaults to 1. Values above one process
independent PDFs concurrently, while pages within each PDF remain sequential so previous-page
context and resume behavior are preserved. A directory with only one PDF therefore sees no parallel
speedup.

## Explicitly gated live smoke test

Live tests must require both a marker and an opt-in environment value. They run sequentially and do
not benchmark the shared service:

```console
ARCHIVATORIUM_RUN_EINFRA_LIVE=1 \
E_INFRA_API_TOKEN="$(< /secure/path/e-infra-token)" \
uv run pytest -m live_einfra tests/live/test_einfra_smoke.py
```

The test validates structure, capability, completion, redaction, and resume invariants. It must not
snapshot model prose or retain live requests/responses.

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

Before each implementation commit, inspect the working tree and stage only files assigned to the
completed task. Existing unrelated modified tests, local data, scripts, and credentials must remain
unstaged.
