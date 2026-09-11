# Data Model: Unified LLM Providers

## Provider Selection

Represents the user's explicit or default model-service choice for one command run.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `provider` | `ollama` or `e-infra` | Yes | Defaults to `ollama`; never inferred from an endpoint or credential. |
| `command` | `metadata` or `ocr` | Yes | Selects the provider-specific omitted-model default. |
| `endpoint_input` | URL or absent | No | Resolved from the new endpoint option or legacy `--host`; conflicting values are invalid. |
| `model_input` | string or absent | No | An explicit value always wins over a provider default. |
| `credential_file` | path or absent | No | Explicit e-INFRA credential source; never used implicitly. |

### Validation rules

- Provider resolution happens before templates, output directories, preflight scanning, input
  discovery, PDF rendering, or network requests.
- Omitted provider means Ollama with all existing option and environment semantics.
- Provider does not select or change an OCR mode.
- Provider is fixed for the complete command and every retry; it has no fallback transition.

## Model Connection

The validated connection configuration supplied to the shared client factory.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `provider` | provider identifier | Yes | Copied from Provider Selection. |
| `endpoint` | URL or SDK-default sentinel | Yes | e-INFRA default is `https://llm.ai.e-infra.cz/v1/`; Ollama preserves current host resolution. |
| `model` | string | Yes | Provider/command default or explicit override. |
| `timeout_policy` | named policy | Yes | Preserves the existing Ollama structured/OCR distinction; e-INFRA owns its remote policy. |
| `credential_source` | environment, file, DigestAuth, or none | Yes | Metadata only; does not contain the secret itself. |
| `secret` | redacted secret value or absent | No | Excluded from representation, serialization, logs, equality diagnostics, and errors. |

### Default resolution

| Provider | Command | Omitted endpoint | Omitted model |
|----------|---------|------------------|---------------|
| Ollama | metadata | Existing SDK/`--host` behavior | `gemma4:31b` |
| Ollama | OCR | `--host`, then `OLLAMA_HOST`, then `http://localhost:11434` | `qwen3.5:9b` |
| e-INFRA | metadata | `https://llm.ai.e-infra.cz/v1/` | `qwen3.8-27b` |
| e-INFRA | OCR | `https://llm.ai.e-infra.cz/v1/` | `qwen3.8-27b` |

### Credential resolution

```text
e-INFRA selected
  -> explicit --llm-api-key-file supplied?
       -> validate regular/readable/protected file -> trim -> non-empty secret
       -> otherwise read E_INFRA_API_TOKEN -> trim -> non-empty secret
  -> no usable secret -> configuration failure before processing
```

The file source takes precedence over the environment. `OPENAI_API_KEY` and an unselected local
file are never read. Ambient e-INFRA credentials are ignored for Ollama. Existing Ollama user and
password precedence remains independent for OCR, and DigestAuth is used only when both resolve.

## Model Message

A provider-neutral ordered message presented to a model.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `role` | system or user | Yes | Order is stable and preserved by every transport. |
| `text` | string | Yes | Preserved byte-for-byte for Ollama compatibility. |
| `images` | ordered list of local paths | No | Files must exist and be readable before transmission. |

### Provider translation

- Ollama keeps the existing message dictionary shape and image path list.
- e-INFRA converts each image to an in-request base64 data URL content part after capability
  validation.
- Encoding is transport-only; callers never receive provider content-part structures.

## Reasoning Directive

Represents whether a request omits reasoning control, disables reasoning, or chooses an effort.

| Public state | Ollama request | e-INFRA request |
|--------------|----------------|-----------------|
| omitted | no `think` field | no reasoning field |
| disabled | boolean `False` | `reasoning_effort="none"` |
| low | `think="low"` | `reasoning_effort="low"` |
| medium | `think="medium"` | `reasoning_effort="medium"` |
| high | `think="high"` | `reasoning_effort="high"` |

Omission is distinct from disabled. Standard and FireRed OCR retain omission, GLM retains disabled,
and Qwen 3.8 OCR uses the command-scoped choice.

## Generation Options

The requested inference behavior with source information retained for validation.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `temperature` | non-negative number or absent | No | Current validation is preserved. |
| `top_p` | number from 0 through 1 or absent | No | Current validation is preserved. |
| `top_k` | non-negative integer or absent | No | Native Ollama only. |
| `repeat_penalty` | positive number or absent | No | Native Ollama only. |
| `repeat_last_n` | integer at least -1 or absent | No | Native Ollama only. |
| `output_tokens` | positive integer, unlimited sentinel, or absent | No | Ollama keeps `num_predict`; e-INFRA supports positive limits only. |
| `context_tokens` | positive integer or absent | No | Native Ollama only and not exposed as a new remote setting. |
| `explicit_fields` | set of field names | Yes | Distinguishes user overrides from profile defaults for diagnostics. |

Unsupported explicit values or a mode whose required defaults cannot be represented cause a
configuration failure. They are never silently omitted.

## Structured Result Contract

Describes a structured model request without changing existing metadata/tag schemas.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `schema_name` | string | Yes | Stable, provider-safe name derived from the requested model type. |
| `json_schema` | mapping | Yes | Exact Pydantic JSON Schema used for validation. |
| `system_instruction` | string | Yes | Existing fixed structured-extraction instruction. |
| `user_prompt` | string | Yes | Original prompt plus the existing indented schema suffix. |
| `validation_attempts` | positive integer | Yes | Ollama compatibility retains four total attempts for `retries=3`. |

The e-INFRA transport adds its JSON Schema response constraint without changing the prompt. Both
providers return visible JSON to the same cleanup and Pydantic validation path.

## Model Request

The complete immutable request passed from the shared client to one provider transport.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `model` | string | Yes | Fixed across retries. |
| `messages` | ordered Model Message list | Yes | At least one message; order and text remain fixed except the established structured validation correction. |
| `options` | Generation Options | Yes | Validated against provider capability before sending. |
| `reasoning` | Reasoning Directive | Yes | Fixed across retries. |
| `structured_result` | Structured Result Contract or absent | No | Present only for metadata/tagging extraction. |
| `delivery` | complete or incremental | Yes | Ollama remains complete; e-INFRA OCR uses incremental delivery. |

## Model Response

The normalized provider result returned to archival workflows.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `visible_text` | string | Yes | Excludes separately returned private reasoning. |
| `finish_state` | complete, length, interrupted, or failed | Yes | Length/interruption cannot be mistaken for valid completion. |
| `usage` | token counts or absent | No | Diagnostic only; never written into archival output. |
| `provider_request_id` | string or absent | No | May be logged safely for support without headers or secrets. |

OCR passes only `visible_text` into existing normalization. Structured extraction cleans and
validates only `visible_text`. Partial incremental content is held in memory and is never a complete
page until the response finishes successfully.

## Provider Capability

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `model` | string | Yes | Exact selected identifier. |
| `chat` | boolean | Yes | Required for all feature workflows. |
| `multimodal` | boolean or unknown | Yes | Must be true before e-INFRA OCR transmits an image. |
| `structured_output` | boolean or unknown | Yes | Confirmed by transport contract/live smoke for structured calls. |
| `reasoning_efforts` | effort set | Yes | Must contain the requested mapped value. |
| `maximum_output_tokens` | integer or unknown | Yes | Requested allowance must not exceed a known maximum. |

e-INFRA capability data is cached for one command. A model unavailable from the service or known not
to support the requested workload fails before document/page inference. Capability lookup failure
for OCR is a safe failure, not permission to send an image blindly.

## Normalized Model Error

| Category | Retryable | Required outcome |
|----------|-----------|------------------|
| configuration | No | Fail before processing with actionable option/credential guidance. |
| authentication or permission | No | Report provider and category without secret material. |
| invalid request or unknown model | No | Report model and correction guidance. |
| unsupported capability | No | Identify the incompatible workload or option. |
| rate limited | Yes | Honor a bounded retry delay. |
| transient service/connection | Yes | Apply bounded retry policy. |
| truncated or empty remote response | Policy-controlled | Never accept as a completed e-INFRA result. |
| interrupted incremental response | Yes | Discard partial content before retry. |
| structured validation | Yes for established attempts | Preserve corrective prompt behavior. |

Ollama keeps its established provider-specific logging, raised exceptions, retry classes, and empty
OCR response behavior behind the same application-facing interface.

## Ollama Compatibility Baseline

A version-controlled characterization of pre-feature behavior containing:

- resolved CLI/default/environment inputs;
- complete ordered native model requests;
- response and exception fixtures;
- retry count, mutation, and ordering expectations;
- deterministic generated file bytes;
- OCR traversal, resume, page context, and cleanup outcomes.

This baseline is immutable during provider implementation. A difference is a regression unless it
is unrelated elapsed-time or an explicitly accepted pre-existing nondeterministic live-model change.

## Lifecycle

```text
CLI values and environment
  -> Provider Selection
  -> validate endpoint/options/credential source
  -> Model Connection
  -> build one shared client for the command
  -> build provider-neutral Model Request
  -> validate Provider Capability
  -> translate and send through selected transport
  -> assemble provider response
  -> Model Response or Normalized Model Error
  -> existing metadata/tagging/OCR validation and persistence
```

Terminal connection states are `complete` or `failed`. There is no transition from one provider to
another during a command.

