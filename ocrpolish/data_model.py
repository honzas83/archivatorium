from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class LinePattern:
    """Normalized representation of a line of text."""

    normalized_words: frozenset[str]

    def __bool__(self) -> bool:
        return bool(self.normalized_words)


@dataclass
class FrequencyEntry:
    """Tracking data for a recurring line pattern."""

    total_count: int = 0
    file_paths: set[Path] = field(default_factory=set)
    verbatim_counts: dict[str, int] = field(default_factory=dict)

    @property
    def file_count(self) -> int:
        return len(self.file_paths)

    @property
    def most_frequent_verbatim(self) -> str:
        if not self.verbatim_counts:
            return ""
        # Using a lambda to satisfy mypy's type checking for the key argument
        return max(self.verbatim_counts, key=lambda k: self.verbatim_counts[k])


@dataclass(frozen=True)
class ProcessingConfig:
    """Runtime configuration for OCR post-processing."""

    input_dir: Path
    output_dir: Path
    input_mask: str = "*.md"
    protected_prefixes: list[str] = field(default_factory=lambda: ["#", "|", ">"])
    typewriter_width: int = 80
    overwrite: bool = True
    dry_run: bool = False
    save_filtered: bool = True
    filter_file_path: Path | None = None
    frequency_file_path: Path = Path("frequency.txt")
    docx_output_dir: Path | None = None
