# Data Model: Add FireRed OCR Mode

This feature adds one transient request-configuration value. It does not introduce a database, configuration file, or Markdown output schema change.

## OCR Mode Selection

Represents the user's optional `--mode` value.

| Field | Type | Required | Validation | Meaning |
|-------|------|----------|------------|---------|
| `mode` | string | No | `standard`, `glm`, or `firered` | Omitted mode defaults to standard; `firered` resolves to the FireRed profile. |

### State transition

1. CLI input is parsed and validated.
2. Omitted mode or explicit `standard` resolves to the existing standard profile.
3. `glm` resolves to the existing GLM profile.
4. `firered` resolves to the FireRed profile.
5. Any other value terminates before document discovery or rendering.

Mode selection never selects, replaces, or validates the model name.

## OCR Mode Profile

An immutable description of the mode-specific request behavior.

| Field | Type | Standard profile | GLM profile | FireRed profile |
|-------|------|------------------|-------------|-----------------|
| `user_prompt` | string | Existing general OCR prompt | `Text Recognition:` | Exact supplied FireRed Markdown-conversion prompt |
| `system_prompt` | optional string | Existing general OCR system prompt | Absent | Absent |
| `include_previous_page_context` | boolean | `true` | `false` | `false` |
| `think` | optional boolean | Unspecified/absent | `false` | Unspecified/absent |
| `inference_defaults` | settings | Existing defaults | Existing GLM-specific defaults | Existing standard defaults |

The profile deliberately has no model field. It is resolved once for a run and does not change thereafter.

## Page Recognition Request

Represents one remote recognition call for a rendered page.

| Field | Type | FireRed source and invariant |
|-------|------|------------------------------|
| `model` | string | Existing default or `--model`; never set by the profile |
| `messages` | ordered message list | Exactly one user message containing the supplied FireRed prompt and the current page image; no system message or text derived from another page |
| `think` | optional boolean | Omitted, preserving existing standard behavior |
| `options` | mapping | Existing standard effective inference settings, plus any explicit existing override |
| `stream` | boolean | Existing `false` behavior |

### Relationships

- One OCR run has one resolved profile and one independently selected model.
- Every missing or empty page produces one FireRed request under the resolved profile.
- Retries for a page reuse an equivalent request.
- Existing non-empty pages are skipped during resume and create no request.

### Page processing states

`discovered -> recognized-existing -> skipped`

or

`discovered -> missing/empty -> rendered -> request-pending -> recognized -> merged`

On a transient API error:

`request-pending -> retry-wait -> request-pending`

For FireRed, every transition into `request-pending` enforces the exact-prompt and no-other-page-text invariants.
