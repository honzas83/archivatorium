from collections import Counter

from ocrpolish.data_model import ProcessingConfig
from ocrpolish.processor import clean_lines
from ocrpolish.utils.files import ensure_directory_exists, get_output_path, scan_files
from ocrpolish.utils.logging import get_logger


def run_processing(config: ProcessingConfig) -> None:
    """Coordinate the OCR post-processing."""
    logger = get_logger()
    
    # Pass 1: Frequency counting
    logger.info("Pass 1: Counting line frequencies globally...")
    line_counts: Counter[str] = Counter()
    files = list(scan_files(config.input_dir, config.input_mask))
    total_files = len(files)
    
    for input_file in files:
        with open(input_file, encoding="utf-8") as f:
            # Use a set to count each line at most once per file
            unique_lines_in_file = {line.strip() for line in f}
            for line in unique_lines_in_file:
                line_counts[line] += 1
                
    # Identify headers/footers based on threshold
    threshold_count = total_files * config.threshold
    
    global_headers = {line for line, count in line_counts.items() 
                      if line and count > threshold_count}
    
    logger.info(f"Identified {len(global_headers)} global headers/footers")
    
    # Pass 2: Cleaning and reformatting
    logger.info("Pass 2: Cleaning and reformatting files...")
    for input_file in files:
        output_path = get_output_path(input_file, config.input_dir, config.output_dir)
        ensure_directory_exists(output_path)
        
        with open(input_file, encoding="utf-8") as f:
            lines = f.readlines()
            
        cleaned = clean_lines(lines, global_headers, config)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(cleaned) + "\n")
            
        logger.debug(f"Processed {input_file} -> {output_path}")

    logger.info("Processing complete")
