import re

from ocrpolish.data_model import ProcessingConfig


def should_protect_line(line: str, protected_prefixes: list[str]) -> bool:
    """Check if a line starts with a protected markdown prefix."""
    trimmed = line.lstrip()
    # Also protect standard document structures like ANNEX or APPENDIX
    extra_protected = ["ANNEX", "APPENDIX"]
    if any(trimmed.upper().startswith(p) for p in extra_protected):
        return True
    return any(trimmed.startswith(p) for p in protected_prefixes)

def is_page_number(line: str) -> bool:
    """Check if a line matches a page numbering pattern."""
    patterns = [
        r"^#\s*Page\s+\d+$",        # # Page 3
        r"^\d+-\d+$",                # 1-1
        r"^Page\s+\d+$",             # Page 3
        r"^\d+$"                     # 3
    ]
    return any(re.match(p, line.strip(), re.IGNORECASE) for p in patterns)

def merge_paragraphs(lines: list[str], config: ProcessingConfig) -> list[str]:
    """Merge lines into paragraphs while respecting protected prefixes and typewriter width."""
    processed_lines: list[str] = []
    current_paragraph: list[str] = []
    
    for line in lines:
        stripped = line.strip()
        raw_line = line.rstrip("\n")
        
        if not stripped:
            if current_paragraph:
                processed_lines.append(" ".join(current_paragraph))
                current_paragraph = []
            if processed_lines and processed_lines[-1] != "":
                processed_lines.append("")
        elif should_protect_line(line, config.protected_prefixes):
            if current_paragraph:
                processed_lines.append(" ".join(current_paragraph))
                current_paragraph = []
            processed_lines.append(line.rstrip())
        elif len(raw_line) > config.typewriter_width:
            # This is a whole unwrapped paragraph
            if current_paragraph:
                processed_lines.append(" ".join(current_paragraph))
                current_paragraph = []
            processed_lines.append(stripped)
        else:
            # Wrapped line, should be merged
            current_paragraph.append(stripped)
            
    if current_paragraph:
        processed_lines.append(" ".join(current_paragraph))
    return processed_lines

def clean_lines(lines: list[str], global_headers: set[str], config: ProcessingConfig) -> list[str]:
    """Perform header/footer removal and paragraph merging."""
    # First pass: Filter out headers/footers (except page numbers)
    filtered_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped in global_headers and not is_page_number(stripped):
            continue
        filtered_lines.append(line)
        
    if not filtered_lines:
        return []
        
    processed_lines = merge_paragraphs(filtered_lines, config)
        
    # Final cleanup: ensure exactly one empty line between paragraphs
    final_output: list[str] = []
    for line in processed_lines:
        if not line:
            if final_output and final_output[-1] != "":
                final_output.append("")
        else:
            final_output.append(line)
            
    return final_output
