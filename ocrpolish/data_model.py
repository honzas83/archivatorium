from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ProcessingConfig:
    """Runtime configuration for OCR post-processing."""
    input_dir: Path
    output_dir: Path
    input_mask: str = "*.md"
    threshold: float = 0.5
    protected_prefixes: list[str] = field(default_factory=lambda: ["-", "*", "#", "|", ">"])
    typewriter_width: int = 80
    overwrite: bool = True
