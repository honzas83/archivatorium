import shutil
from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from archivatorium.processor import FrequencyStore


FREQUENCY_THRESHOLD = 5


def initialize_vault_from_template(template_dir: Path, output_dir: Path) -> None:
    """
    Initializes an Obsidian vault in output_dir by copying all
    files from template_dir.
    """
    if not template_dir.exists():
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    for item in template_dir.rglob("*"):
        if item.is_file():
            # Skip common OS junk
            if item.name == ".DS_Store":
                continue

            rel_path = item.relative_to(template_dir)
            dst = output_dir / rel_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dst)


def scan_files(input_dir: Path, mask: str = "*.md") -> Iterator[Path]:
    """Recursively scan input_dir for files matching the mask, excluding sidecar .filtered.md files."""
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    for path in input_dir.rglob(mask):
        if not path.name.endswith(".filtered.md"):
            yield path


def get_output_path(input_file: Path, input_dir: Path, output_dir: Path) -> Path:
    """Calculate the mirrored output path for a given input file."""
    relative_path = input_file.relative_to(input_dir)
    return output_dir / relative_path


def ensure_directory_exists(path: Path) -> None:
    """Ensure the directory for the given path exists."""
    path.parent.mkdir(parents=True, exist_ok=True)


def get_filtered_path(output_path: Path) -> Path:
    """Calculate the sidecar .filtered.md path for a given output path."""
    return output_path.with_suffix(output_path.suffix + ".filtered.md")


def generate_frequency_report(report_path: Path, store: "FrequencyStore") -> None:
    """Write the consolidated frequency report to the specified path."""
    # Filter entries with total_count > FREQUENCY_THRESHOLD and sort by total_count descending
    entries = [
        entry for entry in store.patterns.values() if entry.total_count > FREQUENCY_THRESHOLD
    ]
    entries.sort(key=lambda x: x.total_count, reverse=True)

    ensure_directory_exists(report_path)
    with open(report_path, "w", encoding="utf-8") as f:
        for entry in entries:
            line = f"{entry.total_count} ({entry.file_count}): {entry.most_frequent_verbatim}\n"
            f.write(line)
