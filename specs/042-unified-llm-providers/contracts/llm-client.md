# Contract: Shared LLM Client

## Boundary

`MetadataProcessor`, `TaggingService`, and `OCREngine` consume one shared model-access contract.
They may choose prompts, schemas, OCR profile behavior, and workflow-level recovery, but they must
not construct SDK clients, authentication headers, provider content parts, schema response fields,
or provider-specific response parsers.

The boundary exposes two operations:

```text
extract_structured(prompt, schema, retries, model, reasoning) -> validated model
generate_text(request) -> visible ModelResponse
```

An Ollama compatibility facade may retain the historical class and constructor name during
migration, but production consumers ultimately type against this shared contract.

## Structured extraction

Inputs:

- original user prompt;
- requested Pydantic model type;
- total validation retry allowance using the existing public meaning;
- optional per-call model override;
- provider-neutral reasoning directive.

Shared behavior:

1. Build the existing fixed structured system instruction.
2. Append two newlines, `Strictly follow this JSON schema:\n`, and the schema serialized with
   indentation level two to the user prompt.
3. Request temperature zero and the provider's structured-result constraint.
4. Extract and trim visible content.
5. If content begins with a Markdown fence, remove the existing optional lowercase `json` opener and
   closing fence.
6. Validate with the requested Pydantic model.
7. On a validation failure, append the existing corrective text and retry up to the configured
   total; preserve all other request semantics.

For the compatibility default `retries=3`, Ollama permits four total attempts. Non-validation
Ollama exceptions remain immediate. e-INFRA transient errors use its separate bounded transport
policy without changing the logical structured-validation allowance.

The e-INFRA request includes JSON Schema response format and an 8,192-token initial allowance.
Ollama retains native `format=<schema>` and receives no new output limit.

## Text and image generation

The request contains:

- exact ordered messages;
- zero or more ordered local image paths;
- selected model;
- reasoning directive, including distinct omitted and disabled states;
- validated common and provider-native inference options;
- delivery preference.

The response contains only:

- visible text;
- completion state;
- optional safe request identifier;
- optional token usage.

Private reasoning is never returned as visible text. The existing OCR `</think>` cleanup remains
after this boundary as a defensive compatibility rule.

## Transport obligations

### Native Ollama transport

- Use native Ollama Chat.
- Preserve complete current kwargs, including message dictionary shape and image path strings.
- Preserve `stream=False`.
- Preserve the 300-second structured timeout and 240-second OCR timeout.
- Preserve native reasoning boolean/string/omission and all current native options.
- Accept current dictionary and object response shapes.
- Preserve current retry/logging behavior defined by the Ollama compatibility contract.

### e-INFRA transport

- Use OpenAI-compatible Chat Completions at the resolved base URL.
- Authenticate with the resolved Bearer token without exposing it.
- Disable implicit SDK retries so the shared policy owns call counts.
- Translate images to base64 data URL content parts.
- Translate disabled reasoning to `none` and named effort unchanged.
- Use JSON Schema response format for structured extraction.
- Use positive remote output allowances and recognize reasoning-token exhaustion.
- Stream OCR, append each visible delta once in order, ignore reasoning deltas, and report the final
  completion state.
- Discard all buffered content when a stream fails before successful completion.

## Capability contract

All requests require chat capability. e-INFRA OCR additionally requires verified multimodal
capability for the exact selected model. Capability data may be obtained once and cached for the
command. Known unsupported capability, unknown model, or unavailable capability data fails safely
before image transmission.

The initial `qwen3.8-27b` capability contract is:

```text
chat: required
multimodal: required for OCR
structured JSON: validated by provider tests and opt-in smoke test
reasoning: none, low, medium, high
maximum output: 32768 tokens
```

## Normalized errors

| Error | Retry rule |
|-------|------------|
| Configuration | Never retry |
| Authentication/permission | Never retry |
| Invalid request | Never retry |
| Unknown model | Never retry or substitute |
| Unsupported capability/option | Never retry |
| Rate limit | Bounded retry honoring a bounded `Retry-After` |
| Timeout/connection/transient server | Bounded retry |
| Interrupted e-INFRA stream | Discard buffer, then bounded retry |
| Truncated e-INFRA output | Report distinctly; retry only under explicit bounded policy |
| Empty e-INFRA visible output | Never accept as success |
| Structured validation | Use established corrective validation retry |

Every retry repeats the same provider, model, messages, image, reasoning, and inference semantics.
No error can trigger provider fallback.

Errors and logs must redact credentials, headers, secret-bearing configurations, and private
reasoning. Safe diagnostics include provider, model, status/category, request ID, document/page, and
remediation.

## Persistence boundary

- Structured results reach existing metadata/tagging validation and rendering only after successful
  Pydantic validation.
- OCR text reaches existing normalization and page assembly only after a complete response.
- Partial remote content never marks a page or document complete.
- Provider identity, usage, request ID, and reasoning are not added to archival output.

## Concurrency

This feature keeps sequential model calls. The boundary must not introduce background parallelism.
Any later concurrency control must cap e-INFRA requests at four per account unless current service
documentation states a different limit.

