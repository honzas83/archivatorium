import argparse
import sys
from pathlib import Path

from ocrpolish.core import run_processing
from ocrpolish.data_model import ProcessingConfig
from ocrpolish.utils.logging import setup_logging


def parse_args(args: list[str]) -> ProcessingConfig:
    """Parse CLI arguments into a ProcessingConfig."""
    parser = argparse.ArgumentParser(
        description="Clean LLM-OCR output by removing headers/footers and reformatting paragraphs."
    )
    
    parser.add_argument("input_dir", type=Path, help="Directory containing raw OCR markdown files.")
    parser.add_argument(
        "output_dir", type=Path, help="Directory where processed files will be saved."
    )
    
    parser.add_argument(
        "--mask", 
        type=str, 
        default="*.md", 
        help="Glob pattern for files to process (default: *.md)."
    )
    
    parser.add_argument(
        "--threshold", 
        type=float, 
        default=0.5, 
        help="Frequency threshold (0.0-1.0) for header/footer detection (default: 0.5)."
    )
    
    parser.add_argument(
        "--width", 
        type=int, 
        default=80, 
        help="Typewriter width. Lines longer than this are wrapped (default: 80)."
    )
    
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Increase output verbosity."
    )
    
    parsed = parser.parse_args(args)
    
    return ProcessingConfig(
        input_dir=parsed.input_dir,
        output_dir=parsed.output_dir,
        input_mask=parsed.mask,
        threshold=parsed.threshold,
        typewriter_width=parsed.width
    )

def main() -> None:
    """Main entry point for the CLI."""
    try:
        config = parse_args(sys.argv[1:])
        setup_logging(verbose=True)  # Hardcoding verbose for development
        run_processing(config)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
