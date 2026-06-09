# Research: Canonical Tag Data Layer

## Summary of Decisions

This document outlines the design decisions and technical specifications for parsing, validating, normalizing, and consuming canonical generated tags in OCRPolish.

---

## 1. Canonical Tag Syntax & Regex Matching

### Decisions
1. **Authoritative Prefixes**: The parser will only recognize tags starting with the following prefixes:
   - `#Entities/` (for entities State, Org, City, Person)
   - `#Topics/` (for taxonomy paths)
   - `#Tags/` (for conceptual flat tags)
2. **Obsolete/Legacy Tags**: All other tags (e.g. `#Nuclear-Deterrence` or legacy `#Category/Category-Name`) will be ignored. Legacy tags MUST NOT be supported.
3. **Regex Pattern**: We will match hashtags using:
   `r"#(Entities|Topics|Tags)/[a-zA-Z0-9_/-]+"`
   This captures the prefix and the path. To handle trailing punctuation (e.g. in parentheses `(#Entities/Org/NATO)` or at sentence end `#Tags/Planning.`), we will match the word character boundary and strip trailing slashes, dots, and hyphens.

---

## 2. Structured Tag Model (`CanonicalTags`)

### Decisions
1. **Data Model**: The structured model will be represented by a Python class `CanonicalTags` (defined in `ocrpolish/models/metadata.py` or `ocrpolish/utils/tag_parser.py`).
2. **Properties**:
   - `conceptual_tags: set[str]` — Normalized conceptual tags (e.g. `{"tactical-weapons"}`).
   - `topics: set[str]` — Normalized hierarchical topic paths (e.g. `{"category/subtopic"}`).
   - `entities: dict[str, set[str]]` — Entities grouped by type:
     - `State`: set of state names (e.g. `{"france"}`)
     - `Org`: set of organization names (e.g. `{"nato"}`)
     - `City`: set of nested state/city paths (e.g. `{"united-kingdom/london"}`)
     - `Person`: set of person names (e.g. `{"luns"}`)
   - `raw_paths: set[str]` — Complete normalized paths (without the leading `#`) to allow exact reconstruction (e.g. `{"Entities/State/France", "Topics/Category/Subtopic", "Tags/Conceptual-Tag"}`).
3. **Reconstruction**: Rendering helpers will add `#` back to the paths in `raw_paths` (e.g. `f"#{path}"`) when writing back to Markdown.

---

## 3. Tag Normalization & Strict Validation

### Decisions
1. **Normalization**: For each matched tag:
   - Strip leading `#`.
   - Split the path by `/`.
   - Apply `normalize_tag_component` from `ocrpolish/utils/nlp.py` to each component.
   - Reassemble with `/`.
2. **Validation**:
   - **Prefix Check**: Must start with `Entities/`, `Topics/`, or `Tags/`.
   - **Component Count Check**:
     - `Entities/State`: Must have exactly 3 components (e.g. `Entities`, `State`, `<name>`).
     - `Entities/Org`: Must have exactly 3 components (e.g. `Entities`, `Org`, `<name>`).
     - `Entities/Person`: Must have exactly 3 components (e.g. `Entities`, `Person`, `<name>`).
     - `Entities/City`: Must have exactly 4 components (e.g. `Entities`, `City`, `<state>`, `<city>`).
     - `Topics`: Must have at least 2 components (e.g. `Topics`, `<taxonomy-path>...`).
     - `Tags`: Must have exactly 2 components (e.g. `Tags`, `<tag>`).
   - **Empty Value Check**: Any component that is empty after normalization is invalid.
3. **Diagnostics**: Any tag failing validation is ignored and logs a warning:
   `logger.warning("Malformed generated tag ignored: %s", raw_tag)`

---

## 4. Resume-Safe Preflight Scan & Reconciled Counters

### Decisions
1. **Legacy Counter Replacement**: The existing fields `self.tag_counts`, `self.state_counts`, `self.org_counts`, and `self.city_counts` in `MetadataProcessor` will be replaced with counters derived only from the new canonical parser.
2. **In-Memory Registry**: To ensure resume safety and prevent double-counting or leakage across runs, `MetadataProcessor` will maintain:
   - `scanned_files_tags: dict[Path, CanonicalTags]` — Maps output file path to its parsed tags.
   - Global counters:
     - `conceptual_tag_counts: Counter[str]`
     - `topic_counts: Counter[str]`
     - `entity_counts: dict[str, Counter[str]]` (keys: State, Org, City, Person)
3. **Preflight Scan Flow**:
   - Before processing any files, run `preflight_scan(output_dir)` once.
   - For each existing `.md` output file:
     - Read and parse it with `CanonicalTagParser`.
     - Record its tags in `scanned_files_tags[file_path]`.
     - Update the global counters with these tags.
4. **Incremental/Overwrite Update Flow**:
   - If a file is skipped (output exists and `overwrite` is `False`):
     - It does not run LLM processing. It already contributes to counters from the preflight scan, so we do nothing.
   - If a file is processed/overwritten:
     - If the file exists in `scanned_files_tags` (from preflight), **subtract** its old tags from the global counters.
     - Run LLM/metadata generation.
     - Parse the newly generated Markdown file.
     - **Add** its new tags to the global counters.
     - Update `scanned_files_tags[file_path]` with the new tags.

---

## 5. Downstream Indexing & XLSX Refactoring

### Decisions
1. **Indexing Integration**: `IndexingService` (in `ocrpolish/services/indexing_service.py`) will parse Markdown files using `CanonicalTagParser` instead of reading the frontmatter `tags` list and regexing the body directly.
2. **Structured Retrieval**:
   - States index will pull directly from `entities["State"]`.
   - Cities index will pull directly from `entities["City"]` (parsed state/city structure).
   - Orgs index will pull directly from `entities["Org"]`.
   - Topics index will pull directly from `topics`.
3. **XLSX Column Export**:
   - Since tags are no longer part of YAML frontmatter, the XLSX report will dynamically load columns for tags/entities from the parsed structured model.
   - The XLSX columns will include:
     - `conceptual_tags` (comma-separated list, e.g. `Conceptual-Tag, Another-Tag`)
     - `topic_tags` (comma-separated list, e.g. `Topics/Category/Subtopic`)
     - `state_entities` (comma-separated list)
     - `org_entities` (comma-separated list)
     - `city_entities` (comma-separated list)
     - `person_entities` (comma-separated list)
