# Data Model: Preserve Metadata Directory Structure

## Mirroring Logic

### Entities

- **Source File**: Any file residing within the input directory tree.
- **Target File**: The corresponding file in the output directory tree.

### File Types & Actions

| File Extension | Action | Implementation |
|----------------|--------|----------------|
| `.md`          | Enrich | Read as UTF-8 (errors='replace'), extract metadata, write as UTF-8. |
| `.pdf`         | Mirror | Attempt `os.link` to `target_dir/pdf/filename.pdf`. |
| Other          | Mirror | Attempt `os.link` to `target_dir/filename`. |

### Validation Rules

- **Directory Creation**: Parent directories in the target tree MUST be created before any file operation.
- **UTF-8 Safety**: All written Markdown files MUST be valid UTF-8.
- **Atomic Operations**: (Optional) Write to temp and rename? Given the scale, direct write to target is usually acceptable unless robustness is critical. We will stick to direct write as per existing patterns.

## Directory Mapping

The mapping function `f(path, input_dir, output_dir)` is defined as:
`target_path = output_dir / path.relative_to(input_dir)`
