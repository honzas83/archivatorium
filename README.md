# archivatorium

A specialized toolkit for cleaning, formatting, and validating OCR outputs processed by Large Language Models (LLMs).

## Features

- **Precision Tagging System**: A three-tiered tagging system (Conceptual, Entity, Topic) using flat production topic extraction for high accuracy and signal.

## Obsidian Export Structure

The `metadata` command generates Markdown files with a specific structure designed for Obsidian:

1. **YAML Frontmatter**: Contains core metadata such as `title`, `summary`, `pages`, `intent`, `date`, `archive_code`, and `source` (`[[pdf/<filename>.pdf]]`).
2. **Abstract Callout**: A block containing:
   - The document **title** and **abstract**.
   - **Mentioned Entities**: Hierarchical tags for mentioned states, organizations, cities, and people (e.g., `State/UK`, `Org/NATO`, `City/UK/London`, `Person/Andrae/K-W`).
   - **Categories/Topics**: Hierarchical tags extracted from a provided NATO taxonomy.
   - **Tags**: Flat, canonical conceptual keywords (e.g., `#NuclearStrategy`).

### Metadata Prerequisites
The metadata extraction feature requires [Ollama](https://ollama.com/) to be installed and running locally.
```bash
ollama pull gemma4:31b
```

## Usage

The toolkit provides several primary commands for processing documents: `ocr`, `clean`, `metadata`, and `interlink`.

### 1. OCR Processing (Ollama VLM)
Converts multipage PDF files in `INPUT_DIR` recursively to Markdown files in `OUTPUT_DIR` using a local VLM (Ollama). Includes on-the-fly rendering and incremental per-page recovery/resumption.

```bash
archivatorium ocr [OPTIONS] INPUT_DIR OUTPUT_DIR
```

#### Options
- `--host TEXT`: URL for the Ollama server (or environment variable `OLLAMA_HOST`).
- `--user TEXT`: DigestAuth username (or environment variable `OLLAMA_USER`).
- `--password TEXT`: DigestAuth password (or environment variable `OLLAMA_PASSWORD`).
- `--model TEXT`: The VLM model name to use (default: `qwen3.5:9b`).
- `--mode [standard|qwen38|glm|firered]`: OCR request profile (default: `standard`). Standard mode preserves the existing prompts and previous-page context; Qwen 3.8 uses its dedicated Markdown transcription prompt; GLM uses the native `Text Recognition:` prompt, disables thinking, and recognizes every page independently; FireRed uses its Markdown-conversion prompt and recognizes every page without previous-page context.
- `--model-think [False|low|medium|high]`: Case-insensitive Qwen 3.8 reasoning effort (default: `medium`). `False` disables reasoning. Standard and FireRed continue to omit reasoning, and GLM continues to disable it regardless of this option.
- `--temperature FLOAT`: Override the selected mode's temperature (`>= 0`).
- `--top-p FLOAT`: Override top-p sampling (`0..1`).
- `--top-k INTEGER`: Override top-k sampling (`>= 0`).
- `--repeat-penalty FLOAT`: Override repetition penalty (`> 0`).
- `--repeat-last-n INTEGER`: Override how many recent tokens are checked for repetition (`-1` means the full context, `0` disables the check; GLM default: `512`).
- `--num-predict INTEGER`: Override maximum output tokens (`-1` or `>= 1`).
- `--dpi INTEGER`: DPI for page rendering (default: `300`).
- `--no-page-header`: Do not include `---\n\n# Page N\n\n` markers in the output (Note: this disables page-level resuming).

*Note: Requires system package `poppler` (e.g. `brew install poppler` on macOS or `apt-get install poppler-utils` on Linux).*

GLM mode requires an Ollama API server version 0.9.0 or newer. Mode selection and model selection are independent; select the actual remote model with `--model`:

```bash
archivatorium ocr \
  --host http://ollama.example:11434 \
  --mode glm \
  --model glm-ocr \
  INPUT_DIR OUTPUT_DIR
```

Without overrides, GLM mode sends `temperature=0.0`, `top_p=0.00001`, `top_k=1`, `repeat_penalty=1.1`, `repeat_last_n=512`, and `num_predict=8192`. The wider repetition window helps prevent runaway duplication of longer OCR passages. Explicit inference options replace only their corresponding mode defaults.

FireRed mode keeps the selected model and existing inference defaults, but sends its dedicated prompt without a system message or text from another page:

```bash
archivatorium ocr \
  --host http://ollama.example:11434 \
  --mode firered \
  --model firered-ocr \
  INPUT_DIR OUTPUT_DIR
```

For Qwen 3.8 OCR with reasoning disabled:

```bash
archivatorium ocr INPUT_DIR OUTPUT_DIR \
  --mode qwen38 \
  --model-think False
```

### 2. Cleaning OCR Text
Removes headers/footers and reformats paragraphs.

```bash
archivatorium clean [OPTIONS] INPUT_DIR OUTPUT_DIR
```

#### Options
- `--mask TEXT`: Glob pattern for files to process (default: `*.md`).
- `--width INTEGER`: Typewriter width for wrapping (default: `80`).
- `--dry-run`: Identify boilerplate without writing primary output files.
- `--no-filtered`: Disable generation of `.filtered.md` sidecar files.
- `--frequency-file PATH`: Path for the consolidated frequency report within `OUTPUT_DIR` (default: `frequency.txt`).
- `--docx PATH`: Generate DOCX files alongside Markdown files.
- `--filter-file PATH`: Path to a text file containing phrases to filter out.

### 3. Extracting Metadata
Extracts structured data and flat production topics using a local LLM.

```bash
archivatorium metadata INPUT_DIR OUTPUT_DIR --hierarchy-file topics/NATO_themes.yaml --tags-file topics/USEFUL_TAGS.yaml [OPTIONS]
```

#### Options
- `--model TEXT`: The Ollama model to use (default: `gemma4:31b`).
- `--model-think [False|low|medium|high]`: Case-insensitive reasoning effort for primary metadata extraction and conditional final-date extraction (default: `medium`). Tag extraction remains non-thinking.
- `--mask TEXT`: Glob pattern for Markdown files to enrich (default: `*.md`). Non-matching Markdown files are not sent to metadata or tagging enrichment.
- `--overwrite`: Overwrite existing files in output directory.
- `--hierarchy-file`: Required path to a YAML topic hierarchy (e.g., `topics/NATO_themes.yaml`).
- `--tags-file`: Required path to a YAML file containing useful tags (e.g., `topics/USEFUL_TAGS.yaml`).
- `--vault-root PATH`: Optional Obsidian vault root; defaults to `OUTPUT_DIR`.
- `--pdf-dir PATH`: Optional source PDF lookup directory; defaults to `OUTPUT_DIR`.
- `--citekey-mode {stem,path}`: Deterministic citekey mode.
- `--dry-run`: Scan inputs and report planned metadata actions.

#### Selecting the NATO Topic Taxonomy

The original taxonomy remains available and unchanged. Select it explicitly for reproducible v1
processing:

```bash
archivatorium metadata INPUT_DIR OUTPUT_V1 \
  --hierarchy-file topics/NATO_themes.yaml \
  --tags-file topics/USEFUL_TAGS.yaml
```

The revised taxonomy is opt-in. Rerun metadata extraction from the source documents and write to a
separate output directory:

```bash
archivatorium metadata INPUT_DIR OUTPUT_V2 \
  --hierarchy-file topics/NATO_themes_v2.yaml \
  --tags-file topics/USEFUL_TAGS.yaml
```

V2 applies a universal substantive-subject rule: a topic must be an important subject of the
document, not merely a keyword, entity, meeting, citation, title, or passing reference. Weak matches
are omitted, and an empty thematic-topic list is valid.

Archivatorium does not migrate or rewrite v1 topic paths. The v2 hierarchy contains narrower and
split concepts, so adopting it requires reclassification through a fresh metadata run.

#### Person Entity Paths

New metadata runs store people surname-first as
`#Entities/Person/<surname>[/<given-name-or-initials>]`. For example, K-W Andrae and K. W. Andrae
both become `#Entities/Person/Andrae/K-W`, while Joseph M.A.H. Luns becomes
`#Entities/Person/Luns/Joseph-M-A-H`. If the given name is unknown, the surname-only form such as
`#Entities/Person/Andrae` is valid. Titles, ranks, and roles such as minister or secretary are not
included in the path.

Existing Person tags are not migrated automatically. Rerun `metadata` to generate the new
hierarchy, optionally selecting a reasoning effort:

```bash
archivatorium metadata INPUT_DIR OUTPUT_V2 \
  --hierarchy-file topics/NATO_themes_v2.yaml \
  --tags-file topics/USEFUL_TAGS.yaml \
  --model-think high
```

Generated PDFs are mirrored into a `pdf/` folder beside the generated Markdown file, and generated Markdown links to them as `[[pdf/<filename>.pdf]]`.

### 4. Interlinking Obsidian Vault
Post-processes a generated Obsidian vault in-place to cross-link documents using archive codes, generate indices, and export metadata.

```bash
archivatorium interlink [OPTIONS] VAULT_DIR
```

#### Options
- `--dry-run`: Logs changes without writing.
- `--verbose`: Show detailed matching logs.
- `--force`: Regenerate all links, even if they already exist.
- `--unifications PATH`: Path to custom unification rules YAML.

## Development

Run quality checks:
```bash
ruff check .
mypy .
pytest
```
