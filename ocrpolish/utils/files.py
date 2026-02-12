from collections.abc import Iterator
from pathlib import Path


def scan_files(input_dir: Path, mask: str = "*.md") -> Iterator[Path]:
    """Recursively scan input_dir for files matching the mask."""
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    
    return input_dir.rglob(mask)

def get_output_path(input_file: Path, input_dir: Path, output_dir: Path) -> Path:
    """Calculate the mirrored output path for a given input file."""
    relative_path = input_file.relative_to(input_dir)
    return output_dir / relative_path

def ensure_directory_exists(path: Path) -> None:
    """Ensure the directory for the given path exists."""
    path.parent.mkdir(parents=True, exist_ok=True)
