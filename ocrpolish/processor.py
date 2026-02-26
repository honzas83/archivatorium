import re
import textwrap
from pathlib import Path

from ocrpolish.data_model import FrequencyEntry, ProcessingConfig
from ocrpolish.utils.nlp import get_word_set


class FrequencyStore:
    """Store for tracking line pattern frequencies across multiple files."""

    def __init__(self) -> None:
        self.patterns: dict[frozenset[str], FrequencyEntry] = {}

    def update(self, line: str, file_path: Path) -> None:
        """Update frequency data with a new line from a file."""
        stripped = line.strip()
        if not stripped:
            return

        # Ignore structural markers (page numbers, etc.) in frequency report
        if is_structural_marker(stripped):
            return

        words = get_word_set(stripped)
        if not words:
            return

        if words not in self.patterns:
            self.patterns[words] = FrequencyEntry()

        entry = self.patterns[words]
        entry.total_count += 1
        entry.file_paths.add(file_path)
        entry.verbatim_counts[stripped] = entry.verbatim_counts.get(stripped, 0) + 1


def load_filter_list(filter_file_path: Path | None) -> set[frozenset[str]]:
    """Load and normalize filter patterns from a file."""
    if not filter_file_path or not filter_file_path.exists():
        return set()

    filters = set()
    with open(filter_file_path, encoding="utf-8") as f:
        for line in f:
            words = get_word_set(line)
            if words:
                filters.add(words)
    return filters


def should_protect_line(line: str, protected_prefixes: list[str]) -> bool:
    """Check if a line starts with a protected markdown prefix."""
    trimmed = line.lstrip()

    # Check if it looks like a list marker - we WANT to wrap these now
    # - bullet, * bullet, 1. numbered
    if re.match(r"^([\-\*\+]|\d+\.)\s+", trimmed):
        return False

    # Explicitly allow wrapping for tag-like markup even if it's in protected_prefixes
    if trimmed.startswith("<") or trimmed.startswith("["):
        return False

    # Also protect standard document structures like ANNEX or APPENDIX
    extra_protected = ["ANNEX", "APPENDIX"]
    if any(trimmed.upper().startswith(p) for p in extra_protected):
        return True

    return any(trimmed.startswith(p) for p in protected_prefixes)


def is_structural_marker(line: str) -> bool:
    """Check if a line matches a structural pattern that MUST be preserved."""
    patterns = [
        r"^#\s*Page\s+\d+$",  # # Page 3
        r"^-\s*\d+\s*-$",  # -1- or - 5 -
    ]
    return any(re.match(p, line.strip(), re.IGNORECASE) for p in patterns)


def format_markdown_table(table_lines: list[str]) -> list[str]:
    """Format a list of table lines to have aligned columns."""
    rows = []
    for line in table_lines:
        content = line.strip()
        if content.startswith("|"):
            content = content[1:]
        if content.endswith("|"):
            content = content[:-1]
        cells = [cell.strip() for cell in content.split("|")]
        rows.append(cells)

    if not rows:
        return []

    num_cols = max(len(row) for row in rows)
    col_widths = [0] * num_cols

    # First pass: find max width per column
    for row in rows:
        for i, cell in enumerate(row):
            if i < num_cols:
                # Don't let separator lines influence width calculation
                if not all(c in "-:" for c in cell) or len(cell) == 0:
                    col_widths[i] = max(col_widths[i], len(cell))

    # Minimum width for standard markdown separators
    col_widths = [max(w, 3) for w in col_widths]

    # Second pass: format lines with padding and alignment
    formatted_lines = []
    for row in rows:
        formatted_cells = []
        for i in range(num_cols):
            cell_text = row[i] if i < len(row) else ""
            if all(c in "-:" for c in cell_text) and len(cell_text) > 0:
                # It's a separator line: |---|---|
                left = ":" if cell_text.startswith(":") else "-"
                right = ":" if cell_text.endswith(":") else "-"
                # Total width including padding spaces is col_widths[i] + 2
                middle = "-" * (col_widths[i] + 2 - 2)
                formatted_cells.append(f"{left}{middle}{right}")
            else:
                formatted_cells.append(f" {cell_text.ljust(col_widths[i])} ")
        formatted_lines.append("|" + "|".join(formatted_cells) + "|")

    return formatted_lines


def is_table_separator(line: str) -> bool:
    """Check if a line is a markdown table separator (e.g., |---|---|)."""
    stripped = line.strip()
    if not stripped:
        return False
    # Remove all characters that are valid in a separator
    # If the line contains ONLY | - : and whitespace, it's a separator
    # but it MUST contain at least one dash to distinguish from just pipes.
    if "-" not in stripped:
        return False

    # Remove leading/trailing pipes if present
    content = stripped
    if content.startswith("|"):
        content = content[1:]
    if content.endswith("|"):
        content = content[:-1]

    # After removing pipes, it should only have dashes, colons, and pipes
    remaining = content.replace("-", "").replace(":", "").replace("|", "").replace(" ", "")
    return len(remaining) == 0


def is_table_line(line: str) -> bool:
    """Check if a line looks like it belongs to a table (contains a pipe)."""
    return "|" in line


def wrap_lines(lines: list[str], config: ProcessingConfig) -> list[tuple[list[str], bool]]:
    """Wrap long lines. Returns list of (wrapped_lines, did_wrap) tuples."""
    blocks: list[tuple[list[str], bool]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        raw_line = line.rstrip("\n")

        if not stripped:
            blocks.append(([], False))
            i += 1
            continue

        # Handle tables separately: group consecutive table lines
        # Lookahead to detect a table even if the first line doesn't start with |
        is_table = False
        if stripped.startswith("|"):
            is_table = True
        elif i + 1 < len(lines) and is_table_line(stripped) and is_table_separator(lines[i + 1]):
            is_table = True

        if is_table:
            table_lines = []
            # Gather all consecutive lines that look like table lines
            while i < len(lines):
                current_stripped = lines[i].strip()
                # A table ends at a blank line or a line that clearly isn't a table line
                if not current_stripped or not is_table_line(current_stripped):
                    break
                table_lines.append(lines[i])
                i += 1

            if table_lines:
                formatted_table = format_markdown_table(table_lines)
                blocks.append((formatted_table, False))
                continue

        # Standard line processing
        if should_protect_line(line, config.protected_prefixes):
            blocks.append(([line.rstrip()], False))
        elif len(raw_line) > config.typewriter_width:
            wrapped = textwrap.wrap(stripped, width=config.typewriter_width, subsequent_indent="")
            blocks.append((wrapped, len(wrapped) > 1))
        else:
            blocks.append(([stripped], False))
        i += 1

    return blocks


def is_filtered_line(line: str, filter_list: set[frozenset[str]]) -> bool:
    """Check if a line matches any filter in the filter list."""
    stripped = line.strip()
    if not stripped:
        return False

    if is_structural_marker(stripped):
        return False

    current_word_set = get_word_set(stripped)
    n_words = len(current_word_set)
    if n_words == 0:
        return False

    for f_set in filter_list:
        intersection = current_word_set.intersection(f_set)
        if len(intersection) >= 0.5 * n_words:
            return True
    return False


def filter_lines(lines: list[str], filter_list: set[frozenset[str]]) -> tuple[list[str], list[str]]:
    """Split lines into filtered (kept) and dropped based on filter list."""
    filtered_lines = []
    dropped_lines = []

    for line in lines:
        if is_filtered_line(line, filter_list):
            dropped_lines.append(line)
        else:
            filtered_lines.append(line)

    return filtered_lines, dropped_lines


def format_blocks(blocks: list[tuple[list[str], bool]]) -> list[str]:
    """Join wrapped blocks with appropriate blank line separation."""
    final_output: list[str] = []
    for block, did_wrap in blocks:
        if not block:
            # If we encounter an empty line in the source, ensure we have one in output
            if final_output and final_output[-1] != "":
                final_output.append("")
        else:
            # Add the block content
            final_output.extend(block)

            # Rule: add empty newline after it if it was wrapped by the tool
            if did_wrap:
                final_output.append("")

    # Remove trailing empty line if added by the last block's wrap
    if final_output and final_output[-1] == "":
        final_output.pop()

    return final_output


def clean_lines(
    lines: list[str], filter_list: set[frozenset[str]], config: ProcessingConfig
) -> tuple[list[str], list[str]]:
    """Perform filtering and paragraph wrapping. Returns (cleaned, dropped)."""
    filtered_lines, dropped_lines = filter_lines(lines, filter_list)

    if not filtered_lines:
        return [], dropped_lines

    blocks = wrap_lines(filtered_lines, config)
    final_output = format_blocks(blocks)

    return final_output, dropped_lines
