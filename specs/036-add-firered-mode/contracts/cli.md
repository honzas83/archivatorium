# CLI Contract: FireRed OCR Mode

## Command

```text
archivatorium ocr [OPTIONS] INPUT_DIR OUTPUT_DIR
```

The existing two directory arguments, recursive PDF discovery, mirrored Markdown output, resume, retry, and page-order semantics are unchanged.

## Mode option

| Option | Type | Default | Validation | Effect |
|--------|------|---------|------------|--------|
| `--mode [standard|glm|firered]` | choice | `standard` | Only the three listed values are accepted | Selects the existing standard or GLM profile, or the FireRed prompt and page-isolation policy. |

All existing OCR options, including `--model` and inference overrides, retain their names and behavior. Mode selection is independent of model selection.

## FireRed request contract

Command:

```bash
archivatorium ocr --mode firered --model firered-ocr INPUT_DIR OUTPUT_DIR
```

For each page that requires recognition, the request contains one user message with the current page image and exactly this content:

```text
You are an expert in converting PDF images to Markdown format.

Please convert the provided document image into Markdown while preserving the original document structure.

Requirements:
- Preserve headings, paragraphs, lists, and reading order.
- Convert tables to HTML table format.
- Convert mathematical formulas to LaTeX.
- Ignore figures and images.
- Do not add, summarize, correct, or infer any content that is not present in the document.
- Output only the converted Markdown.
```

The request contains no generic system message, no previous-page OCR text, and no textual context derived from a previous, next, or other page. FireRed does not set a model name, thinking value, or new inference defaults; existing choices and defaults apply.

## Compatibility and errors

- Omitting `--mode` or specifying `--mode standard` keeps existing standard prompts and prior-page context behavior.
- `--mode glm` keeps the existing GLM prompt, disabled thinking, default settings, and independent-page behavior.
- An unsupported mode produces Click usage output and a non-zero exit before document discovery, rendering, or recognition begins.
- Remote recognition failures retain the existing retry and error-reporting behavior.
