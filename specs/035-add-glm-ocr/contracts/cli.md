# CLI Contract: GLM OCR Mode

## Command

```text
archivatorium ocr [OPTIONS] INPUT_DIR OUTPUT_DIR
```

The existing two positional directory arguments and recursive processing semantics are unchanged. Options may appear in any position accepted by Click; the canonical examples place them before the positional arguments.

## Existing arguments

- `INPUT_DIR`: Existing directory containing PDFs; recursively searched.
- `OUTPUT_DIR`: Destination for mirrored Markdown output.

## New options

| Option | Type | Default when omitted | Validation | Effect |
|--------|------|----------------------|------------|--------|
| `--mode [standard|glm]` | choice | `standard` | Only `standard` and `glm` are accepted | Selects unchanged standard behavior or GLM prompt, no-context policy, disabled thinking, and GLM defaults. |
| `--temperature FLOAT` | float | Selected-mode default | `>= 0` | Overrides `options.temperature`. |
| `--top-p FLOAT` | float | Selected-mode default | `0..1` inclusive | Overrides `options.top_p`. |
| `--top-k INTEGER` | integer | Selected-mode default | `>= 0` | Overrides `options.top_k`. |
| `--repeat-penalty FLOAT` | float | Selected-mode default | `> 0` | Overrides `options.repeat_penalty`. |
| `--repeat-last-n INTEGER` | integer | Selected-mode default | `>= -1` | Overrides `options.repeat_last_n`; `-1` means `num_ctx`, `0` disables repetition lookback. |
| `--num-predict INTEGER` | integer | Selected-mode default | `-1` or `>= 1` | Overrides `options.num_predict`. |

All existing options, including `--model`, retain their current names and defaults. Inference overrides are also accepted in standard mode; in that case they tune only the named runtime options while standard prompting and previous-page context behavior remain active.

## GLM default request

GLM mode requires an Ollama API server at version 0.9.0 or newer so the server contract can honor explicit `think: false`.

Command:

```bash
archivatorium ocr --mode glm --model glm-ocr INPUT_DIR OUTPUT_DIR
```

The effective remote API request for each page requiring recognition is equivalent to:

```json
{
  "model": "glm-ocr",
  "messages": [
    {
      "role": "user",
      "content": "Text Recognition:",
      "images": ["<current-page-image>"]
    }
  ],
  "think": false,
  "options": {
    "temperature": 0.0,
    "top_p": 0.00001,
    "top_k": 1,
    "repeat_penalty": 1.1,
    "repeat_last_n": 512,
    "num_predict": 8192,
    "num_ctx": "<existing OCR context-window value>"
  },
  "stream": false
}
```

The page image representation is delegated to the existing official client transport. No recognized text from any other page may appear in `messages` or another request field.

## Override example

```bash
archivatorium ocr \
  --mode glm \
  --model custom-glm-ocr \
  --temperature 0.1 \
  --top-p 0.2 \
  --top-k 5 \
  --repeat-penalty 1.2 \
  --repeat-last-n 1024 \
  --num-predict 4096 \
  INPUT_DIR OUTPUT_DIR
```

This changes only the model name and six explicit values. It does not enable thinking, add a system prompt, or add previous-page context.

## Compatibility contract

When `--mode` is omitted or set to `standard` and all six new inference options are omitted:

- the existing system and user prompts are sent;
- existing previous-page context behavior remains active;
- the existing model default is retained;
- the existing inference options and `stream=false` behavior are retained;
- recursive discovery, resume, retry, output format, and page ordering are unchanged.

## Errors

- Unsupported mode, non-numeric option input, or an out-of-range value produces Click usage output and a non-zero exit before OCR processing.
- `--num-predict` accepts `-1` or a positive integer; zero and values below `-1` are rejected.
- `--repeat-last-n` accepts `-1`, zero, or a positive integer; values below `-1` are rejected.
- Remote API failures retain the existing per-document reporting and retry behavior.
- A server older than the documented GLM-mode prerequisite may reject or ignore thinking control and is unsupported for this mode.
- A mode never validates or constrains the model name; model availability errors come from the configured remote API host.
