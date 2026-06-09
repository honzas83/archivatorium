# Quickstart Validation Guide: Idempotent Vault Interlinking

This guide provides step-by-step instructions to validate that the idempotent interlinking and vault-finalization workflow operates correctly.

## Prerequisites

- Python 3.12 installed
- Project dependencies installed (`pip install -e .` from repository root)
- A mock Obsidian vault generated in a directory (e.g. `mock_vault/`) containing a few files with cross-document references and canonical tags.

## Validation Scenarios

### Scenario 1: First-Pass Interlinking and Index/XLSX Generation

1. Prepare a mock vault containing:
   - `doc1.md` with archive code `NPG/D(74)2` and tag `#Entities/State/US`. It references `NPG/D(75)1`.
   - `doc2.md` with archive code `NPG/D(75)1` and tag `#Entities/Org/NATO`. It references `NPG/D(74)2`.
2. Run the interlink command:
   ```bash
   ocrpolish interlink mock_vault
   ```
3. **Verify Outcomes**:
   - `doc1.md` contains a markdown link: `[[doc2.md|NPG/D(75)1]]` (or similar vault-relative path) in its body and/or metadata references.
   - `Index - States.md` is generated and lists `#Entities/State/us` with a link to `doc1.md`.
   - `Index - Organizations.md` is generated and lists `#Entities/Org/nato` with a link to `doc2.md`.
   - `metadata_index.xlsx` is generated in `mock_vault/` containing both documents with their pivoted columns.

### Scenario 2: Idempotent Re-runs (Idempotency Check)

1. Re-run the command on the same vault:
   ```bash
   ocrpolish interlink mock_vault
   ```
2. **Verify Outcomes**:
   - Running `git diff mock_vault` shows no modifications to the files.
   - All links in `doc1.md` and `doc2.md` are intact and not nested (no `[[ [[...]] ]]` or double bracket wrapping).
   - Rows in metadata tables or index files are not duplicated.

### Scenario 3: Exclude Generated Output Files from Scanning

1. Check that the scan log shows only the source files (e.g., `doc1.md`, `doc2.md`) were read.
2. **Verify Outcomes**:
   - Log verifies that `Index - States.md`, `Index - Organizations.md`, and `metadata_index.xlsx` were successfully excluded from the scanned source document list.
