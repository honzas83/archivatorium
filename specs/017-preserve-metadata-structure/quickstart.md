# Quickstart: Preserve Metadata Directory Structure

This feature enhances the `metadata` command to mirror the entire source directory structure to the output directory, using hardlinks for efficiency.

## Usage

To process a directory and preserve its structure:

```bash
ocrpolish metadata source_dir/ output_dir/ --recursive
```

### What happens:
1. `ocrpolish` scans `source_dir/` recursively.
2. For every subfolder in `source_dir/`, a corresponding subfolder is created in `output_dir/`.
3. For every `.md` file:
   - Metadata is extracted using Ollama.
   - The file is enriched with frontmatter and callouts.
   - The result is saved to `output_dir/path/to/file.md`.
4. For every other file (e.g., `.pdf`):
   - A hardlink is created from the source to `output_dir/path/to/file.pdf`.
   - If hardlinks are not supported, the file is copied.

## Benefits
- **Zero Space Overhead**: Hardlinks mean that mirrored PDFs don't take up extra disk space.
- **Organization**: Your Obsidian vault structure is perfectly preserved.
- **UTF-8 Safety**: Input files with bad encoding are handled gracefully, and output is guaranteed to be valid UTF-8.
