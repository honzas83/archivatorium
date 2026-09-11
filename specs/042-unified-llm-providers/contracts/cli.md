# Contract: LLM Provider CLI

## Public syntax

Both model-dependent commands add the same provider options:

```console
archivatorium metadata INPUT_DIR OUTPUT_DIR [existing options] \
  [--llm-provider ollama|e-infra] \
  [--llm-base-url URL] \
  [--llm-api-key-file PATH] \
  [--concurrency N]

archivatorium ocr INPUT_DIR OUTPUT_DIR [existing options] \
  [--llm-provider ollama|e-infra] \
  [--llm-base-url URL] \
  [--llm-api-key-file PATH] \
  [--concurrency N]
```

All existing option spellings remain accepted. `--host` remains an additive legacy alias for the
provider endpoint. It is not removed or repurposed as a credential field.

## Common option behavior

| Option | Omitted behavior | Explicit behavior |
|--------|------------------|-------------------|
| `--llm-provider` | `ollama` | Selects exactly one provider for the complete command. |
| `--llm-base-url` | Provider default/resolution | Selects the provider endpoint. |
| `--host` | Existing Ollama behavior | Endpoint alias retained for compatibility; accepted for either provider. |
| `--llm-api-key-file` | e-INFRA environment lookup; ignored for Ollama | Selects the e-INFRA token file and takes precedence over the environment. |
| `--model` | Provider-and-command default | Overrides the model without changing provider or OCR mode. |
| `--model-think` | Existing `medium` default | Case-insensitive `False`, `low`, `medium`, or `high`. |
| `--concurrency` | `1` | Runs at most N independent command-specific document jobs concurrently; accepts 1 through 4. |

If both endpoint options are supplied, their normalized values must agree; otherwise the command
fails before processing. Trailing slash equivalence may be applied for e-INFRA. Ollama endpoint text
is passed with its current semantics and is not otherwise rewritten.

## Default matrix

| Provider | Command | Endpoint when omitted | Model when omitted |
|----------|---------|-----------------------|--------------------|
| Ollama | metadata | Existing Ollama SDK resolution | `gemma4:31b` |
| Ollama | OCR | `OLLAMA_HOST`, then `http://localhost:11434` | `qwen3.5:9b` |
| e-INFRA | metadata | `https://llm.ai.e-infra.cz/v1/` | `qwen3.8-27b` |
| e-INFRA | OCR | `https://llm.ai.e-infra.cz/v1/` | `qwen3.8-27b` |

An explicit model always wins. Selecting a provider or model never selects an OCR mode; `standard`
remains the omitted OCR mode and `qwen38` remains an explicit mode choice.

## Credential contract

### e-INFRA

Resolution order:

1. `--llm-api-key-file PATH` when supplied.
2. `E_INFRA_API_TOKEN`.
3. Configuration error when neither yields a non-empty token.

The file must exist, be a regular readable file, contain a non-empty value after surrounding
whitespace is removed, and have no group/world permission bits. A literal token CLI option is not
provided. `OPENAI_API_KEY` and a repository `meta-api-key` file are never read implicitly.

### Ollama

- Ambient e-INFRA credential variables are ignored.
- Explicit `--llm-api-key-file` is rejected because it is incompatible with Ollama.
- Metadata preserves current SDK host/environment resolution and has no new authentication path.
- OCR preserves independent CLI-over-environment resolution for `--user`/`OLLAMA_USER` and
  `--password`/`OLLAMA_PASSWORD`.
- OCR constructs DigestAuth only when both resolved values are truthy; existing partial-credential
  behavior remains unchanged.

Explicit `--user` or `--password` is rejected with e-INFRA. Ambient `OLLAMA_*` variables are ignored
when e-INFRA is selected.

## Inference-option compatibility

| OCR option | Ollama | e-INFRA |
|------------|--------|---------|
| `--temperature` | Existing behavior | Supported |
| `--top-p` | Existing behavior | Supported |
| `--top-k` | Existing behavior | Rejected when explicit |
| `--repeat-penalty` | Existing behavior | Rejected when explicit |
| `--repeat-last-n` | Existing behavior | Rejected when explicit |
| positive `--num-predict` | Existing `num_predict` | Remote output allowance |
| `--num-predict=-1` | Existing unlimited sentinel | Rejected |

The existing numeric ranges and validation errors are unchanged. Unsupported values are rejected
before PDF discovery or rendering.

### OCR mode compatibility

| Mode | Ollama | e-INFRA initial support |
|------|--------|-------------------------|
| `standard` | Unchanged | Supported for a compatible multimodal model |
| `qwen38` | Unchanged | Supported and recommended for `qwen3.8-27b` |
| `glm` | Unchanged | Rejected because its required native tuning cannot be represented |
| `firered` | Unchanged | Supported for a compatible multimodal model |

Rejection does not alter mode/model independence: neither selection is silently replaced.

## Reasoning behavior

The public values remain unchanged:

| CLI value | Ollama | e-INFRA |
|-----------|--------|---------|
| `False` | boolean false where the profile sends reasoning | effort `none` |
| `low` | `low` | `low` |
| `medium` | `medium` | `medium` |
| `high` | `high` | `high` |

Standard and FireRed OCR continue to omit reasoning control. GLM continues to force false on Ollama.
Qwen 3.8 uses the command-scoped value on every page and retry. Metadata primary, final-date, and
tagging calls continue to receive the command-scoped value.

## Metadata and OCR concurrency

The default value of one follows the existing code path and preserves unchanged Ollama commands.
Values outside 1 through 4 fail during CLI parsing.

Concurrency schedules independent PDFs, not pages within a PDF. Each PDF therefore retains its own
sequential previous-page context, retry flow, page order, output file, and resume state. If fewer
PDFs are ready than the configured value, actual concurrency is lower. A failure in one PDF is
reported without cancelling other independent jobs.

For metadata, concurrency schedules matching Markdown documents after one preflight scan. Each
worker starts from an isolated copy of that preflight vocabulary and keeps its metadata, conditional
date extraction, tagging windows, validation, and persistence sequential. Non-matching files remain
mirrored without model calls. After successful persistence, the coordinator updates the global
tag/entity/topic counters and file registry. Dry-run performs no parallel model work.

## Validation timing and outcomes

Provider configuration errors occur before:

- output/template initialization;
- metadata preflight or source discovery;
- PDF discovery or rendering;
- model/capability requests.

Configuration failures use normal CLI usage failure. Per-document and per-PDF provider failures keep
the existing top-level continuation behavior after processing has begun. Errors may identify the
provider, model, status category, document, page, and remediation, but never include a token,
Authorization header, secret-bearing object representation, or private reasoning.

The command never falls back to another provider.

## Compatibility examples

These commands retain their established Ollama meaning:

```console
archivatorium metadata INPUT OUTPUT \
  --hierarchy-file topics/NATO_themes.yaml \
  --tags-file topics/USEFUL_TAGS.yaml

archivatorium ocr --host http://localhost:11434 --mode qwen38 INPUT OUTPUT
```

e-INFRA metadata with environment credential:

```console
E_INFRA_API_TOKEN=... archivatorium metadata INPUT OUTPUT \
  --llm-provider e-infra \
  --hierarchy-file topics/NATO_themes.yaml \
  --tags-file topics/USEFUL_TAGS.yaml
```

e-INFRA Qwen 3.8 OCR with an explicit credential file:

```console
archivatorium ocr INPUT OUTPUT \
  --llm-provider e-infra \
  --llm-api-key-file /secure/path/e-infra-token \
  --mode qwen38 \
  --model-think low
```
