# Data Model: OCR Post-Processing

## Entities

### GlobalFrequencyMap
- **Description**: In-memory frequency counts of lines found across all input files.
- **Attributes**:
  - `counts`: Dictionary/Counter mapping `line_text` (string) to `frequency` (int).
  - `total_files`: Integer representing total matching files scanned.

### ProcessingConfig
- **Description**: Runtime configuration derived from CLI arguments.
- **Attributes**:
  - `input_dir`: Path (Source directory).
  - `output_dir`: Path (Destination directory).
  - `input_mask`: String (default `*.md`).
  - `threshold`: Float (default 0.5).
  - `protected_prefixes`: List of strings (`-`, `*`, `#`, `|`, `>`).

### FileState
- **Description**: State maintained while processing an individual file.
- **Attributes**:
  - `lines`: List of strings (current file content).
  - `cleaned_lines`: List of strings (result after transformations).

## Logic Transitions

1. **Pass 1 (Aggregation)**:
   - Walk `input_dir` recursively.
   - Filter by `input_mask`.
   - Update `GlobalFrequencyMap`.

2. **Pass 2 (Transformation)**:
   - Re-walk `input_dir`.
   - Create corresponding `output_dir` structure.
   - Filter lines using `GlobalFrequencyMap`.
   - Merge lines into paragraphs based on `protected_prefixes`.
   - Write to target path.
