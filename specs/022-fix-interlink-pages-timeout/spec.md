# Feature Specification: fix-interlink-pages-timeout

**Feature Branch**: `022-fix-interlink-pages-timeout`

**Created**: 2026-05-25

**Status**: Draft

**Input**: User description: "Now, we will fix the bugs: In interlink command, we should unify (SG) (Staff Group) (StaffGroup) and other references like seen in @archive_codes.txt , be prepared also for other unifications (STUDY) (Study Group) etc. In counting the pages, the number of pages should be calculated based on the number of # Page X headers, not from the last number X. In addition, add a global http timeout (configurable in relevant python file) for Ollama calls (let's say 5 minutes)."

## Clarifications
### Session 2026-05-25
- Q: Where should normalization rules be stored? → A: External YAML file (e.g., `topics/unifications.yaml`)
- Q: Should the "match" part of each rule be a Regular Expression or a simple Literal String? → A: Regular Expressions
- Q: Should these unifications be applied globally to every archive code found, or only to those that follow the NPG(...) pattern? → A: Global (Apply rules to any archive code string)

## User Scenarios & Testing *(mandatory)*

### Scenario 1: Interlink Unification
**Given** a vault with documents having archive codes:
- `NPG(SG)N(72)65`
- `NPG(Staff Group)N(72)65`
- `NPG(StaffGroup)N(72)65`
**When** the `interlink` command is run
**Then** all these documents should be recognized as the same archive code and cross-linked correctly (e.g., as language versions or references).

### Scenario 2: Page Counting Accuracy
**Given** a document with headers:
- `# Page 1`
- `# Page 2`
- `# Page 5` (due to OCR error or skipped pages)
**When** metadata extraction is run
**Then** the `pages` field should be `3` (count of headers), not `5` (last number).

### Scenario 3: Ollama Timeout Configuration
**Given** a slow Ollama server
**When** a request takes longer than the configured timeout (e.g., 5 minutes)
**Then** the `ocrpolish` command should fail gracefully with a timeout error instead of hanging indefinitely.

## Functional Requirements *(mandatory)*

### FR-1: Archive Code Unification
- The `InterlinkingService` MUST normalize group references in archive codes.
- **Rules Storage**: Unification rules MUST be loaded from an external YAML file.
- **CLI Override**: The `interlink` command MUST support a `--unifications` option to specify a custom path for the rules file.
- **Default Path**: If no path is provided, it MUST default to `topics/unifications.yaml`.
- **Rule Format**: Each rule MUST consist of a **Regular Expression** pattern to match and a literal string replacement.
- **Documentation**: The rules file MUST include inline instructions for adding new unifications and maintenance guidelines.
- **Maintenance Threshold**: New OCR prefix typos SHOULD only be added to the default rules if they occur 5 times or more in the target dataset.
- **Refined Rules**: Initial rules MUST handle:
  - **Staff Group**: `\(St[af\.]*f[ -]?Group\)` -> `(SG)`
  - **Study**: `[/-]?(?:Study|Etude|Étude)(?:[ -]?Group)?(?=[(/ -]|$)` -> `(STUDY)`
  - **NPG Prefix Typos**: Verified OCR variants (e.g., `NFG`, `NPC`, `NGP`) appearing >= 5 times.
  - **Series Typos**: `(?:VP|NP|WF|NT)` -> `WP`.

### FR-2: Header-based Page Counting
- The metadata processor MUST calculate the total page count by counting the number of occurrences of the `# Page [Number]` header pattern at the start of a line.
- It MUST NOT rely on the numeric value of the last page header found.

### FR-3: Configurable Ollama Timeout
- The `OllamaClient` MUST support a configurable HTTP timeout.
- The default timeout MUST be set to 300 seconds (5 minutes).
- The timeout SHOULD be configurable via a constant in `ocrpolish/services/ollama_client.py` or an environment variable.

## Success Criteria *(mandatory)*

- `interlink` successfully matches archive codes with different group naming conventions (e.g., `Staff Group` vs `SG`).
- Metadata extraction correctly reports the count of pages based on header occurrences.
- Ollama calls respect the 5-minute timeout.
- All existing tests pass, and new tests verify the bug fixes.

## Key Entities *(optional)*

- **Archive Code**: The unique identifier for a document, now with enhanced normalization rules.
- **Page Header**: A markdown header of level 1 starting with "Page " followed by a number.
- **Unification Rules**: A set of mapping rules (Regex -> Replacement) stored in YAML to translate variant group names to canonical forms.

## Assumptions *(mandatory)*

- Unification rules are primarily focused on NATO-specific archive code conventions found in `archive_codes.txt`.
- Page headers always follow the format `# Page X` where X is a number.

## Out of Scope

- Fixing OCR errors in the page numbers themselves (though the new counting logic mitigates the impact).
- Deep semantic analysis of archive codes beyond the specified unifications.
