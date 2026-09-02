# Contract: Metadata Taxonomy Selection

## CLI interface

V2 uses the existing required option; no new flag or default is introduced:

```console
archivatorium metadata INPUT_DIR OUTPUT_DIR \
  --hierarchy-file topics/NATO_themes_v2.yaml \
  --tags-file topics/USEFUL_TAGS.yaml
```

Selecting `topics/NATO_themes.yaml` continues to select v1. The selected file applies to all Markdown
documents discovered recursively under `INPUT_DIR`, and the existing relative output layout remains
unchanged.

## Compatibility guarantees

- `topics/NATO_themes.yaml` remains byte-for-byte unchanged.
- V2 availability does not alter v1 paths, automatically rewrite archives, or transform existing
  metadata.
- Only paths from the explicitly selected, successfully validated taxonomy may be published.
- Both valid v1 and v2 taxonomies receive the universal substantive-subject prompt policy.
- Invalid or unreadable hierarchy files fail clearly before document classification starts.
- Topic reasons keep their existing response contract; this feature adds no quote verification or
  evidence retry.

## Operational guidance

Run v1 and v2 into separate output directories for comparison. To adopt v2, rerun the metadata
command on the source archive with the v2 hierarchy file rather than transforming v1 output paths.
