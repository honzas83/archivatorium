# ocrpolish Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-02-12

## Active Technologies
- Python 3.12 + `argparse` (CLI), `pathlib` (filesystem), `typing` (type hints) (001-ocr-post-processing)
- Local filesystem (input/output mirroring) (001-ocr-post-processing)
- Python 3.12 + `textwrap` (Python Standard Library) (002-wrap-long-paragraphs)
- Filesystem (input/output mirroring) (002-wrap-long-paragraphs)
- Python 3.12 + click, textwrap, collections.Counter (003-enhanced-filtering-wrapping)
- Filesystem (input/output directories, sidecar `.filtered.md` files) (003-enhanced-filtering-wrapping)
- Python 3.12 + `click`, `textwrap`, `unicodedata` (stdlib), `collections.Counter` (stdlib) (004-rework-filtering-wrapping)
- Filesystem (input/output directories, `.freq.txt` sidecar files) (004-rework-filtering-wrapping)
- Python 3.12 + `click`, `textwrap`, `unicodedata` (stdlib), `collections.Counter` (stdlib), `re` (stdlib) (004-rework-filtering-wrapping)
- Filesystem (input/output directories, consolidated `frequency.txt`) (004-rework-filtering-wrapping)
- Python 3.12 + `python-docx` (New), `argparse`, `pathlib` (005-docx-generation)
- Filesystem (input/output directories) (005-docx-generation)
- Python 3.12 + `python-docx`, `re`, `collections.Counter` (006-docx-header-footer)
- Python 3.12 + `python-docx`, `click`, `re` (007-docx-header-footer-enhancement)
- Python 3.12 + `click`, `ollama` (Python library), `pydantic`, `pyyaml` (008-ollama-metadata-extraction)
- Filesystem (recursive input/output directory mirroring) (008-ollama-metadata-extraction)
- Python 3.12 + `PyYAML`, `re` (stdlib) (020-obsidian-interlink-vault)
- Python 3.12 + `click` (CLI), `pathlib` (filesystem), `typing` (type hints) (001-ocr-post-processing)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

- `ocrpolish clean <input_dir> <output_dir>`: Wrap and filter OCR files.
- `ocrpolish metadata <input_dir> <output_dir>`: Extract metadata using LLM.
- `ocrpolish obsidian <input_dir> <output_dir> --template-dir <template_dir>`: Generate Obsidian vault.
- `ocrpolish index <input_dir> <output_dir>`: Index metadata and generate citations.
- `ocrpolish tag <input_dir> <output_dir> --taxonomy <taxonomy_yaml> --tags <tags_yaml>`: Apply tagging system.
- `ocrpolish interlink <vault_dir> [--force]`: Post-process vault for cross-linking (020). Use `--force` to regenerate existing links.

## Code Style

Python 3.12: Follow standard conventions.

### Metadata & Tagging Constraints
- **Obsidian Compatibility**: All generated tags (Conceptual, Entity, Topic) MUST be Obsidian-safe.
    - **Hyphenation**: Spaces and non-alphanumeric characters are replaced with hyphens (e.g., `Nuclear-Deterrence`).
    - **Casing**: Original casing is preserved.
    - **Consistency**: Taxonomy categories/topics and useful tags are preprocessed using the same normalization.
- **Acronym Preservation**: Generic acronyms (all-caps) must be preserved during Title Case conversion.
- **Two-pass Architecture**: Pass 1 for metadata, Pass 2 for tagging.
- **Title Extraction**:
    - **Language**: Titles MUST be extracted in their ORIGINAL LANGUAGE.
    - **Casing**: Titles MUST use natural casing (English: Title Case, French: Sentence case).
    - **Prohibition**: Strictly NO ALL UPPERCASE for titles.
- **Interlinking**:
    - **Idempotency**: Single-pass regex replacement to avoid link nesting.
    - **Regeneration**: Support `--force` flag to re-resolve and update existing links if better matches are found.
    - **Self-Linking**: Documents MUST NOT link to themselves (using BibTeX-style fuzzy matching for detection).
    - **Flexible Matching**:
        - Archive codes treat `/` and `-` as equivalent separators (OCR mitigation).
        - **BibTeX Fallback**: If no exact match is found, system MUST attempt matching using BibTeX-style keys (e.g., `NPG-D-74-2` matches `NPG/D(74)2`).
        - **Priority Order**:
            1. Exact match in source_lang
            2. BibTeX-style fuzzy match in source_lang
            3. Exact match in English
            4. BibTeX-style fuzzy match in English
            5. Exact match in any lang
            6. BibTeX-style fuzzy match in any lang
    - **Sync & Sort**: References metadata is synchronized with body occurrences and sorted by order of appearance.
    - **Formatting**:
        - Use `<br>` as separator for vertical lists in metadata callouts.
        - **Bold fields**: `title`, `pages`, `date`, and `language` MUST be bolded in the callout.
        - **Non-bold fields**: `language_versions` MUST NOT be bolded.
- **Vault Initialization**:
    - **Template**: System MUST recursively copy ALL files from `obsidian_template` to the output directory (e.g., `index.md`, `.obsidian/` configs).

## Recent Changes
- 020-obsidian-interlink-vault: Implemented idempotent interlinking with flexible code matching and reference synchronization.
- 018-tagging-system: Implemented three-tiered precision tagging (Conceptual, Entity, Topic) using a dynamic two-pass architecture.
- 008-ollama-metadata-extraction: Added Python 3.12 + `click`, `ollama` (Python library), `pydantic`, `pyyaml`
- 007-docx-header-footer-enhancement: Added Python 3.12 + `python-docx`, `click`, `re`
- 006-docx-header-footer: Added Python 3.12 + `python-docx`, `re`, `collections.Counter`


<!-- MANUAL ADDITIONS START -->
- **Repository Integrity:** NEVER add large data files (PDFs, images, or large Markdown datasets) to the repository. Always ensure such directories are ignored via `.gitignore`.
<!-- MANUAL ADDITIONS END -->

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
at [specs/023-canonical-tag-layer/plan.md](specs/023-canonical-tag-layer/plan.md)
<!-- SPECKIT END -->
