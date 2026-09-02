# Contract: Model Reasoning CLI Option

## Public syntax

```console
archivatorium metadata INPUT_DIR OUTPUT_DIR [existing options] --model-think=VALUE
archivatorium ocr INPUT_DIR OUTPUT_DIR [existing options] --model-think=VALUE
```

`VALUE` is case-insensitive and accepts:

| CLI value | Model request value |
|-----------|---------------------|
| `False` | boolean `false` |
| `low` | `"low"` |
| `medium` | `"medium"` |
| `high` | `"high"` |

The default is `medium`. Help output lists the accepted values and default.

Any other value is rejected before input discovery or a model request, with the accepted values in
the error message.

## OCR propagation

- For `--mode=qwen38`, each page request includes the converted model request value.
- With no option, Qwen 3.8 therefore uses `"medium"` instead of its former high setting.
- Standard and FireRed continue to omit the reasoning field.
- GLM continues to use boolean `false`.
- Sampling overrides, model selection, prompts, retries, output, and reasoning-content stripping are
  unchanged.

## Metadata propagation

- Primary document metadata extraction receives the converted value.
- Conditional final-date extraction receives the same converted value.
- Retries performed inside either structured extraction retain the value.
- Tag extraction remains explicitly non-thinking and is outside this option's scope.
- Model selection, prompts, output, overwrite, and dry-run behavior are unchanged.

## Compatibility expectations

- Existing invocations remain syntactically valid.
- Omitting the option intentionally changes only the governed reasoning default to medium.
- The option is command-scoped and is not stored in generated archive metadata.
