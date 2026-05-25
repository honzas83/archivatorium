# Data Model: fix-interlink-pages-timeout

## Configuration

### Ollama Configuration
- **OLLAMA_TIMEOUT**: 300.0 (float, seconds).

### Unification Rules
- **Configuration Path**: `topics/unifications.yaml` (default), overridable via CLI `--unifications`.
- **unifications**: A list of objects.
  - **pattern**: A case-insensitive Regular Expression string.
  - **replacement**: The canonical literal string replacement.

## Unification Logic
1. Load `topics/unifications.yaml` (or custom path).
2. For each rule in the list:
   - Perform `re.sub(pattern, replacement, code, flags=re.IGNORECASE)`.
3. Proceed with standard normalization (removing whitespace, `/` vs `-`).

## Canonical Rules (Initial Set)
- **Staff Group**: Normalizes variants like `Staff-Group` or `ST ff Group` to `(SG)`.
- **Study**: Normalizes `Study/` and French `Etude` to `(STUDY)`.
- **Prefixes**: Normalizes common OCR typos (`NGP`, `NPC`, etc.) appearing **>= 5 times** to `NPG`.
- **Series**: Normalizes `VP`, `WF`, etc., to `WP`.

## Entities
- **UnificationRule**: Encapsulates a regex-based mapping for archive code normalization.
