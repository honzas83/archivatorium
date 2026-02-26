import re
from pathlib import Path

from ocrpolish.data_model import PageMetadata, ProcessingConfig
from ocrpolish.processor import (
    FrequencyStore,
    filter_lines,
    format_blocks,
    is_filtered_line,
    load_filter_list,
    wrap_lines,
)
from ocrpolish.utils.docx_utils import create_docx_from_pages
from ocrpolish.utils.files import (
    ensure_directory_exists,
    generate_frequency_report,
    get_filtered_path,
    get_output_path,
    scan_files,
)
from ocrpolish.utils.logging import get_logger
from ocrpolish.utils.metadata import extract_page_number


def analyze_page_metadata(
    lines: list[str], pdf_page_num: int, filter_list: set[frozenset[str]]
) -> PageMetadata:
    """Analyze a single page for markers and filtered metadata."""
    metadata = PageMetadata(pdf_page_number=pdf_page_num)
    
    # 1. Find all -X- markers
    marker_indices = []
    for idx, line in enumerate(lines):
        if extract_page_number(line) is not None:
            marker_indices.append(idx)
            
    if not marker_indices:
        metadata.body_lines = lines
        return metadata

    first_marker_idx = marker_indices[0]
    last_marker_idx = marker_indices[-1]
    
    metadata.original_page_number = extract_page_number(lines[first_marker_idx])
    
    # Nearness window
    window = 5
    
    to_remove = set(marker_indices)
    
    # If there's only one marker, decide if it's header or footer based on position
    is_only_one = len(marker_indices) == 1
    marker_is_header = True
    if is_only_one:
        # If marker is in the lower half of the page lines, treat it as footer anchor
        if first_marker_idx > len(lines) / 2:
            marker_is_header = False

    # 2. Check near first marker (Header)
    if not is_only_one or marker_is_header:
        search_start = max(0, first_marker_idx - window)
        search_end = min(len(lines), first_marker_idx + window + 1)
        for idx in range(search_start, search_end):
            if idx == first_marker_idx:
                continue
            if is_filtered_line(lines[idx], filter_list):
                # Check if it's closer to the first or last marker
                dist_first = abs(idx - first_marker_idx)
                dist_last = abs(idx - last_marker_idx)
                
                if not is_only_one:
                    if dist_first <= dist_last:
                        if idx < first_marker_idx:
                            metadata.header_left.append(lines[idx].strip())
                        else:
                            metadata.header_right.append(lines[idx].strip())
                        to_remove.add(idx)
                else:
                    if idx < first_marker_idx:
                        metadata.header_left.append(lines[idx].strip())
                    else:
                        metadata.header_right.append(lines[idx].strip())
                    to_remove.add(idx)

    # 3. Check near last marker (Footer)
    if not is_only_one or not marker_is_header:
        search_start = max(0, last_marker_idx - window)
        search_end = min(len(lines), last_marker_idx + window + 1)
        for idx in range(search_start, search_end):
            if idx == last_marker_idx or idx in to_remove:
                continue
            if is_filtered_line(lines[idx], filter_list):
                if idx < last_marker_idx:
                    metadata.footer_left.append(lines[idx].strip())
                else:
                    metadata.footer_right.append(lines[idx].strip())
                to_remove.add(idx)

    # 4. Filter remaining lines for body
    body_lines = []
    for idx, line in enumerate(lines):
        if idx in to_remove:
            continue
        # We still need to filter other lines that aren't metadata
        if is_filtered_line(line, filter_list):
            continue
        body_lines.append(line)
        
    metadata.body_lines = body_lines
    return metadata


def split_into_raw_pages(lines: list[str]) -> list[tuple[int, list[str]]]:
    """Split lines into raw blocks based on # Page N markers."""
    pages = []
    current_page = []
    current_pdf_num = 1
    
    for line in lines:
        trimmed = line.strip()
        match = re.match(r"^#\s*Page\s+(\d+)$", trimmed, re.IGNORECASE)
        if match or trimmed == "---":
            # Only append if there is actual content in the current page
            if any(line_ref.strip() for line_ref in current_page):
                pages.append((current_pdf_num, current_page))
            elif pages:
                # Special case: consecutive markers. 
                # If we have content-less pages, the spec says to include them
                # but only if it's explicitly # Page N.
                # '---' followed by '# Page N' should probably be one page break.
                pass
            
            if match:
                current_pdf_num = int(match.group(1))
            else:
                current_pdf_num += 1
                
            current_page = []
            continue
        current_page.append(line)
        
    if any(line_ref.strip() for line_ref in current_page):
        pages.append((current_pdf_num, current_page))
        
    return pages


def run_processing(config: ProcessingConfig) -> None:
    """Coordinate the OCR post-processing."""
    logger = get_logger()

    # Load filter list
    filter_list = load_filter_list(config.filter_file_path)
    if filter_list:
        logger.info(f"Loaded {len(filter_list)} filter patterns from {config.filter_file_path}")
    else:
        logger.info("No filter file provided or file empty. Proceeding without filtering.")

    freq_store = FrequencyStore()
    files = list(scan_files(config.input_dir, config.input_mask))

    logger.info(f"Processing {len(files)} files...")

    for input_file in files:
        output_path = get_output_path(input_file, config.input_dir, config.output_dir)

        with open(input_file, encoding="utf-8") as f:
            lines = f.readlines()

        # Phase A: Standard MD processing (for .md output)
        filtered_lines, dropped = filter_lines(lines, filter_list)

        for line in filtered_lines:
            freq_store.update(line, input_file)

        if not filtered_lines:
            cleaned = []
        else:
            blocks = wrap_lines(filtered_lines, config)
            cleaned = format_blocks(blocks)

        if not config.dry_run:
            ensure_directory_exists(output_path)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(cleaned) + "\n")
            logger.debug(f"Processed {input_file} -> {output_path}")

        if config.save_filtered and dropped:
            filtered_path = get_filtered_path(output_path)
            ensure_directory_exists(filtered_path)
            with open(filtered_path, "w", encoding="utf-8") as f:
                f.write("\n".join(dropped) + "\n")
            logger.debug(f"Saved filtered lines to {filtered_path}")

        # Phase B: Enhanced DOCX generation
        if config.docx_output_dir and not config.dry_run:
            docx_path = get_output_path(input_file, config.input_dir, config.docx_output_dir)
            docx_path = docx_path.with_suffix(".docx")
            ensure_directory_exists(docx_path)

            raw_pages = split_into_raw_pages(lines)
            processed_pages = []
            
            for pdf_num, page_lines in raw_pages:
                metadata = analyze_page_metadata(page_lines, pdf_num, filter_list)
                
                # Wrap body lines for DOCX specifically
                if metadata.body_lines:
                    blocks = wrap_lines(metadata.body_lines, config)
                    metadata.body_lines = format_blocks(blocks)
                
                processed_pages.append(metadata)

            create_docx_from_pages(processed_pages, docx_path)
            logger.debug(f"Generated DOCX with enhanced headers/footers: {docx_path}")

    # Pass 2: Generation of Frequency Report (AFTER all processing)
    logger.info("Generating consolidated frequency report...")
    report_path = config.frequency_file_path
    if not report_path.parents or report_path.parent == Path("."):
        report_path = config.output_dir / report_path

    generate_frequency_report(report_path, freq_store)
    logger.info(f"Frequency report saved to {report_path}")

    logger.info("Processing complete")
