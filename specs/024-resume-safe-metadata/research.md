# Phase 0 Research: Resume-Safe Metadata and Prompt Isolation

This document details the design choices and rationale for implementing resume-safe processing, prompt isolation, deterministic citekey generation, and metadata reconciliation in `ocrpolish`.

## 1. Resume-Safe Preflight Scan Strategy

### Decision
Perform a single preflight scan of the output directory before starting the file processing loop. The scan parses existing Markdown files using the `CanonicalTagParser` to populate the processor's global counters (`conceptual_tag_counts`, `topic_counts`, `entity_counts`) and populates a cache (`scanned_files_tags`) mapping paths to their parsed tags.
When a file is skipped (because `overwrite=false` and its output already exists), its tags are verified against the cache. If they are already in the cache (which is true for all files found in the preflight scan), they are not added again. If for some reason a skipped file is not in the cache, it is parsed and added to the counters to ensure completeness.

### Rationale
- High performance: Scanning files once at startup prevents redundant filesystem reads in the loop.
- Accuracy: Prevents double-counting of tags when files are skipped or re-processed.

### Alternatives Considered
- **No preflight scan**: Scan skipped files inside the loop. Rejected because it results in repeated disk I/O and slower execution when processing large directories.

---

## 2. Clean Source Text Extraction & Section Stripping (Prompt Isolation)

### Decision
Before building prompts for the metadata and tagging LLMs, the system must clean the input content by stripping all previously generated sections:
1. YAML frontmatter (everything between the opening `---` and closing `---` at the top of the file).
2. The Metadata callout block: blockquote sections starting with `> [!info] Metadata` or `> [!Metadata]`.
3. The Abstract callout block: blockquote sections starting with `> [!abstract]`.
4. The Citation callout block: blockquote sections starting with `> [!citing this document]`.
5. Any other generated callouts.

The LLM is prompted only with the cleaned Markdown content, ensuring no generated fields are fed back into its context.

### Rationale
- Completely avoids "hallucination loops" where the LLM repeats previously extracted values or becomes biased by its own historical outputs.
- Keeps the LLM context size compact, saving prompt tokens and processing time.

### Alternatives Considered
- **Including frontmatter but instructing LLM to ignore it**: Rejected because LLMs are highly sensitive to structured context and often hallucinate or repeat existing fields despite negative instructions.

---

## 3. Deterministic Citekey Generation

### Decision
Derive the BibTeX citekey (`citekey` field) programmatically rather than via the LLM:
- **Default mode**: Use the output filename stem (e.g., `stem` of `003-user-auth.md` -> `003-user-auth`).
- **Optional path mode** (`--citekey-mode path`): Use the full vault-relative output path without the `.md` suffix (e.g., `folder/subfolder/003-user-auth`).
- In both cases, the key is normalized with `safe_identifier()` to keep only safe characters (`a-z, A-Z, 0-9, -, _, :`), replacing other characters with hyphens.
- The `archive_code` is kept strictly as archive metadata and never used as the citekey.

### Rationale
- Prevents citekey collisions (especially across folders when using the optional path-based mode).
- Ensures citekeys conform strictly to safe BibTeX formats.

### Alternatives Considered
- **LLM-generated citekey**: Rejected because the LLM cannot guarantee uniqueness or strict character safety across a large dataset.
- **Using archive_code as citekey**: Rejected because archive codes often contain unsafe BibTeX characters (like parentheses, slashes) and cannot guarantee uniqueness across different documents.

---

## 4. Deterministic Metadata Reconciliation

### Decision
Merge manually corrected user frontmatter with newly extracted metadata post-extraction based on explicit rules:
- **Custom fields**: Preserved completely.
- **Title, Sender, Recipient, Intent, Author Name, Author Institution, Date, Archive Code, Language, Location City, Location State**: Preserve the existing value if it is non-empty (giving priority to manual user corrections).
- **Summary**: Overwritten with newly extracted one-sentence summary to enforce length constraints.
- **Pages, Source, Citekey**: Overwritten with newly calculated programmatic values.
- **References**: Set union of existing and newly extracted references, sorted alphabetically.

### Rationale
- Preserves manual corrections made by human editors.
- Ensures system-wide updates (like new citekey format or updated one-sentence summaries) are propagated correctly.
- Prevents previously generated metadata from leaking into LLM context.
