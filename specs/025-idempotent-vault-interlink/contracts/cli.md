# CLI Contract: `ocrpolish interlink`

This contract defines the input/output boundaries and behavior of the `interlink` CLI command.

## Command Signature

```bash
ocrpolish interlink VAULT_DIR [OPTIONS]
```

### Arguments

- `VAULT_DIR` (Required): Path to the generated Obsidian vault directory. Must be an existing directory.

### Options

- `--dry-run`: Log planned modifications to standard error/logs without modifying files.
- `--verbose`: Enable detailed log output during scanning and link resolution.
- `--force`: Force regeneration of all links, references, and language version associations, even if they appear already resolved.
- `--unifications PATH`: Path to a custom YAML file containing archive code unification patterns. Defaults to `topics/unifications.yaml`.

## Exit Codes

- `0`: Success. The vault was scanned, documents were interlinked safely, indices and the spreadsheet export were successfully generated.
- `1`: Validation or parameter error (e.g., `VAULT_DIR` does not exist or is not a directory).
- `2`: Internal processing error (e.g., file write failure or unhandled exception).

## Expected Outputs

Upon successful execution, the following files will be created or overwritten inside `VAULT_DIR`:
1. `metadata_index.xlsx` (pivoted metadata and tag spreadsheet)
2. `Index - States.md`
3. `Index - Cities.md`
4. `Index - Organizations.md`
5. `Index - People.md`
6. `Index - Topics.md`
7. `Index - Tags.md`
