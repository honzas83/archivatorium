# Research: Preserve Metadata Directory Structure

## Decision: Robust Mirroring Strategy
To preserve the directory structure while optimizing for space, we will use a recursive traversal that mirrors every file from the source to the target.

### Hardlinks vs. Copying
- **Choice**: Use `os.link(src, dst)` where possible.
- **Rationale**: Hardlinks are instantaneous and consume no additional disk space for the file data.
- **Fallback**: If `os.link` fails (e.g., cross-device boundary, filesystem not supporting links), use `shutil.copy2(src, dst)` to preserve metadata (timestamps).
- **Modification**: Files that require enrichment (Markdown files) MUST NOT be hardlinked, as they will be modified. They will be read from source and written to target.

## Decision: Valid UTF-8 Enforcement
To address the requirement "Take care of not producing invalid UTF-8 files", we will implement strict encoding/decoding rules.

### Reading
- **Approach**: Use `encoding='utf-8'` with `errors='replace'`.
- **Rationale**: If a source file contains invalid UTF-8 sequences, `errors='replace'` will substitute them with the Unicode replacement character (`\ufffd`). This prevents the application from crashing on bad input while still allowing processing of the rest of the file.

### Writing
- **Approach**: Always write with `encoding='utf-8'`.
- **Rationale**: Python 3 strings are Unicode. Writing them as UTF-8 ensures a valid UTF-8 output file.
- **Safety**: By using `errors='replace'` during reading, we ensure that no invalid byte sequences are present in the string representation before writing.

## Decision: Scope of Processing
- **Current Logic**: The `MetadataProcessor` extracts metadata from `.md` files.
- **New Logic**: 
  - Scan all files in the input directory.
  - If a file is NOT a `.md` file, hardlink/copy it to the target.
  - If a file IS a `.md` file, process it (enrich) and write to target.
  - Special case: If a `.pdf` file is encountered, should we extract metadata from it? 
    - The user said "but the MD files will be enriched". 
    - However, existing logic in `processor_metadata.py` has some PDF-related hooks (e.g. `pdf_dir`). 
    - For now, we will stick to mirroring PDFs and enriching MDs. If a PDF needs metadata extraction, it should be converted to MD first (existing workflow).

## Technical Details

### Hardlink Implementation
```python
def mirror_file(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)
```

### UTF-8 Robustness
```python
content = input_file.read_text(encoding="utf-8", errors="replace")
# ... process ...
output_file.write_text(new_content, encoding="utf-8")
```

## Alternatives Considered
- **Detecting Encoding**: Using libraries like `chardet`. Rejected because UTF-8 is the project standard and `errors='replace'` is simpler and safer for producing valid (if slightly degraded) output.
- **`shutil.copytree`**: Rejected because we need fine-grained control over which files are linked vs. processed.
