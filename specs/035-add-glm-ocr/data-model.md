# Data Model: Add GLM OCR Mode

This feature adds transient request-configuration entities only. No database, configuration file, or Markdown schema changes are introduced.

## OCR Mode Selection

Represents the user's optional `--mode` value.

| Field | Type | Required | Validation | Meaning |
|-------|------|----------|------------|---------|
| `mode` | string | No | `standard` or `glm` | Defaults to the standard VLM profile; `glm` resolves to the GLM profile. |

### State transition

1. CLI input is parsed and validated.
2. Omitted mode or explicit `standard` resolves to the internal standard profile.
3. `glm` resolves to the internal GLM profile.
4. Any other value terminates before document discovery or rendering.

Mode selection never reads or changes the selected model.

## OCR Mode Profile

An immutable internal description of request behavior.

| Field | Type | Standard profile | GLM profile |
|-------|------|----------------|-------------|
| `user_prompt` | string | Existing OCR user prompt | Exact `Text Recognition:` |
| `system_prompt` | optional string | Existing OCR system prompt | Absent |
| `include_previous_page_context` | boolean | `true` | `false` |
| `think` | optional boolean | Unspecified/absent | `false` |
| `inference_defaults` | Inference Settings | Existing request defaults | Six required GLM defaults |

The profile deliberately has no `model` field. It is selected once when the engine is configured and remains unchanged for the run.

## Inference Overrides

Captures values explicitly supplied by the user. Every field is optional so omission remains distinguishable from zero.

| Field | Type | Validation |
|-------|------|------------|
| `temperature` | optional float | `>= 0` |
| `top_p` | optional float | `0 <= value <= 1` |
| `top_k` | optional integer | `>= 0` |
| `repeat_penalty` | optional float | `> 0` |
| `repeat_last_n` | optional integer | `>= -1`; `-1` means `num_ctx`, `0` disables repetition lookback |
| `num_predict` | optional integer | `-1` or `>= 1` |

## Effective Inference Settings

The complete options sent for a page after resolution.

### Resolution rule

1. Start with the selected mode profile's defaults.
2. Replace only fields whose CLI override is not `None`.
3. Retain the existing context-window option independently of these six fields.

### GLM defaults

| Field | Default |
|-------|---------|
| `temperature` | `0.0` |
| `top_p` | `0.00001` |
| `top_k` | `1` |
| `repeat_penalty` | `1.1` |
| `repeat_last_n` | `512` |
| `num_predict` | `8192` |

Standard resolution with no new overrides must reproduce the existing options exactly.

## Page Recognition Request

Represents one call to the remote Ollama chat API.

| Field | Type | Source | GLM invariant |
|-------|------|--------|---------------|
| `model` | string | Existing default or `--model` | Never supplied by the mode profile |
| `messages` | ordered message list | Mode profile and current page image | Exactly one user message; no system or neighboring-page text |
| `think` | optional boolean | Mode profile | Explicitly `false` |
| `options` | mapping | Effective Inference Settings | Contains all six effective GLM values |
| `stream` | boolean | Existing request behavior | `false` |

### Relationships

- One OCR run has one resolved mode profile, one selected model, and one override set.
- The profile plus overrides produce one effective inference setting set for the run.
- Every page requiring recognition creates one page request using those settings.
- Retries for a page reuse equivalent messages and request values.
- Recognized pages found during resume create no page request.

### Page processing states

`discovered -> recognized-existing -> skipped`

or

`discovered -> missing/empty -> rendered -> request-pending -> recognized -> merged`

On a transient API error:

`request-pending -> retry-wait -> request-pending`

In GLM mode, all transitions into `request-pending` enforce the no-neighbor-context invariant.
