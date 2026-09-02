# Contract: Tag-Inference Reasoning

## CLI

The metadata command retains one case-insensitive option:

```text
--model-think=[False|low|medium|high]
```

Default: `medium`.

Conversion:

| CLI spelling | Request value |
|---|---|
| `False` in any case | boolean `False` |
| `low` in any case | string `"low"` |
| `medium` in any case | string `"medium"` |
| `high` in any case | string `"high"` |

Invalid values fail before document processing.

## Propagation

The converted value is command-scoped and is supplied unchanged to:

- primary metadata extraction;
- conditional final-date extraction;
- the single tag-inference request for a short document; or
- every existing tag-inference window for a long document.

The feature changes request configuration only. It adds no ranking, validation, provenance, or
follow-up model request.
