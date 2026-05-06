import os
import re
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml  # type: ignore

from ocrpolish.data_model import PageMetadata


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """
    Parses YAML frontmatter from a string.
    Only consumes the frontmatter if it is a valid YAML dictionary.

    Args:
        content: The content of the file.

    Returns:
        A tuple containing (metadata_dict, body_content).
    """
    if not content.startswith("---"):
        return {}, content

    # Split by lines that are exactly '---'
    parts = re.split(r"^---\s*$", content, maxsplit=2, flags=re.MULTILINE)

    expected_parts = 3
    if len(parts) < expected_parts:
        # Not a complete frontmatter block
        return {}, content

    try:
        metadata = yaml.safe_load(parts[1])
        if isinstance(metadata, dict):
            return metadata, parts[2].lstrip()
    except yaml.YAMLError:
        pass

    # If not a dict or failed to parse, it's just content that happens to have ---
    return {}, content


def stringify_frontmatter(metadata: dict[str, Any]) -> str:
    """
    Converts a dictionary to a YAML frontmatter string.
    """
    if not metadata:
        return ""

    yaml_str = yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True)
    return f"---\n{yaml_str}---\n"


def prepend_frontmatter(content: str, metadata: dict[str, Any]) -> str:
    """
    Prepends metadata as YAML frontmatter to content, merging with existing if present.
    Always ensures a clean frontmatter block delimited by '---'.
    """
    existing_metadata, body = parse_frontmatter(content)
    merged_metadata = {**existing_metadata, **metadata}

    if not merged_metadata:
        return content

    yaml_str = yaml.safe_dump(merged_metadata, sort_keys=False, allow_unicode=True)

    # Standard Obsidian frontmatter format
    return f"---\n{yaml_str}---\n{body.lstrip()}"


def flatten_metadata(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    """
    Recursively flattens a nested dictionary, joining keys with underscores.
    """
    items: list[tuple[str, Any]] = []
    for k, v in data.items():
        new_key = f"{prefix}_{k}" if prefix else k
        if isinstance(v, dict):
            items.extend(flatten_metadata(v, new_key).items())
        else:
            items.append((new_key, v))
    return dict(items)


def normalize_obsidian_tags(tags: list[str]) -> list[str]:
    """
    Normalizes tags for Obsidian YAML frontmatter:
    - Removes '#' prefix.
    - Removes spaces (if any left).
    - Prefixes numeric-only tags with 'Year'.
    """
    normalized = []
    for tag in tags:
        # Strip whitespace first, then remove '#'
        clean_tag = tag.strip().lstrip("#")
        # Remove internal spaces just in case
        clean_tag = clean_tag.replace(" ", "")

        # Prefix numeric tags with 'Year'
        if clean_tag.isdigit():
            clean_tag = f"Year{clean_tag}"

        if clean_tag:
            normalized.append(clean_tag)
    return normalized


def normalize_tag_component(component: str) -> str:
    """
    Normalizes a tag component by stripping whitespace and replacing spaces with hyphens.
    """
    return component.strip().replace(" ", "-")


def format_hierarchical_tag(category: str, *topics: str) -> str:
    """
    Formats a category and one or more topics into an Obsidian hierarchical tag.
    Example: format_hierarchical_tag("City", "UK", "London") -> "#City/UK/London"
    """
    components = [normalize_tag_component(category)]
    components.extend([normalize_tag_component(t) for t in topics if t])
    return f"#{'/'.join(components)}"


def format_as_callout(text: str, title: str = "Abstract", callout_type: str = "abstract") -> str:
    """
    Formats text as an Obsidian callout.
    """
    if not text:
        return ""

    lines = text.strip().splitlines()
    callout_lines = [f"> [!{callout_type}] {title}"]
    callout_lines.extend([f"> {line}" for line in lines])
    return "\n".join(callout_lines) + "\n\n"


class FileMetadataAnalyzer:
    """Analyzes metadata patterns across all pages of a single file."""

    def __init__(self, threshold: float = 0.8):
        self.threshold = threshold

    def analyze(self, pages: list[PageMetadata]) -> set[frozenset[str]]:
        """Identify boilerplate patterns across multiple pages."""
        pattern_counts: Counter[str] = Counter()
        total_pages = len(pages)

        for page in pages:
            # Check headers and footers
            patterns = set()
            patterns.update(page.header_left)
            patterns.update(page.header_right)
            patterns.update(page.footer_left)
            patterns.update(page.footer_right)

            for p in patterns:
                pattern_counts[p] += 1

        # Keep patterns that appear in more than threshold% of pages
        threshold_count = total_pages * self.threshold
        frequent_patterns = {
            frozenset([p]) for p, count in pattern_counts.items() if count >= threshold_count
        }

        return frequent_patterns


def extract_page_number(line: str) -> int | None:
    """Extract page number from a line like '- 5 -' or '~ 5 ~'."""
    match = re.search(r"[-~]\s*(\d+)\s*[-~]", line)
    if match:
        return int(match.group(1))
    return None


def extract_last_page_header(content: str) -> int | None:
    """
    Extracts the page number from the last header matching '# Page [Number]'.
    """
    matches = re.findall(r"^# Page (\d+)", content, re.MULTILINE)
    if matches:
        return int(matches[-1])
    return None


def extract_abstract_tags(content: str) -> list[str]:
    """
    Extracts hierarchical tags from the [!abstract] callout block.
    """
    # 1. Extract the abstract block
    # Matches > [!abstract] followed by any number of lines starting with >
    abstract_match = re.search(
        r"^> \[!abstract\].*?\n((?:>.*\n?)*)", content, re.MULTILINE | re.IGNORECASE
    )
    if not abstract_match:
        return []

    abstract_text = abstract_match.group(1)

    # 2. Extract tags from the block
    # Pattern for hierarchical tags: #Prefix/Component...
    # We look for # followed by letters/digits and /
    tags = re.findall(r"#[a-zA-Z0-9][a-zA-Z0-9/-]*", abstract_text)
    return sorted(list(set(tags)))


def _parse_author(author_name: str) -> tuple[str, str, str]:
    if not author_name:
        return "[Unknown Author]", "[Unknown]", "[U.]"
    parts = author_name.strip().split()
    if len(parts) == 1:
        return parts[0], "", f"{parts[0][0]}." if parts[0] else ""
    first = " ".join(parts[:-1])
    last = parts[-1]
    initials = " ".join(f"{p[0]}." for p in parts[:-1])
    return first, last, initials


def _parse_date(date_str: str) -> tuple[str, str, str, str]:
    if not date_str:
        return "n.d.", "n.d.", "", ""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%Y/%m/%d"), str(dt.year), dt.strftime("%B"), str(dt.day)
    except ValueError:
        try:
            dt = datetime.strptime(date_str, "%Y")
            return f"{dt.year}/01/01", str(dt.year), "January", "01"
        except ValueError:
            return date_str, date_str, "", ""


def format_chicago_citation(data: dict[str, Any]) -> str:
    """Formats metadata into Chicago citation style."""
    first, last, _ = _parse_author(data.get("author_name", ""))
    date_chicago, _, _, _ = _parse_date(data.get("date", ""))
    
    author_str = f"{first}, {last}" if last else first
    title = data.get("title", "Untitled")
    inst = data.get("author_institution", "")
    code = data.get("archive_code", "")
    platform = data.get("platform_name", "NATO Archive Obsidian")
    
    safe_id = safe_identifier(code)
    url = data.get("url", f"https://nato-obsidian.kky.zcu.cz/{safe_id}")
    urldate = data.get("url_date", "")

    main_part = f"{author_str}, “{title},” {date_chicago}"
    
    parts = []
    if inst:
        parts.append(inst)
    if code:
        parts.append(code)
    parts.append(platform)
    if url:
        parts.append(url)
    if urldate:
        parts.append(urldate)
    
    if parts:
        return main_part + ", " + ", ".join(parts) + "."
    return main_part + "."


def format_harvard_citation(data: dict[str, Any]) -> str:
    """Formats metadata into Harvard citation style."""
    first, last, initials = _parse_author(data.get("author_name", ""))
    _, year, _, _ = _parse_date(data.get("date", ""))
    
    author_str = f"{last}, {initials}" if last else first
    title = data.get("title", "Untitled")
    inst = data.get("author_institution", "")
    code = data.get("archive_code", "")
    platform = data.get("platform_name", "NATO Archive Obsidian")
    
    safe_id = safe_identifier(code)
    url = data.get("url", f"https://nato-obsidian.kky.zcu.cz/{safe_id}")
    urldate = data.get("url_date", "")

    main_part = f"{author_str} ({year}). “{title},”"
    
    parts = []
    if inst:
        parts.append(inst)
    if code:
        parts.append(code)
    parts.append(platform)
    if url:
        parts.append(url)
    if urldate:
        parts.append(urldate)
    
    if parts:
        return main_part + " " + ", ".join(parts) + "."
    return main_part


def safe_identifier(key: str) -> str:
    """
    Normalizes a key for BibTeX and URLs by replacing unsafe characters with hyphens.
    Safe characters: a-z, A-Z, 0-9, -, _, :
    """
    if not key:
        return "unknown"
    # Replace anything not a-z, A-Z, 0-9, -, _, : with a hyphen
    safe_key = re.sub(r"[^a-zA-Z0-9\-_:]", "-", key)
    # Collapse multiple hyphens and strip from ends
    return re.sub(r"-+", "-", safe_key).strip("-")


def format_bibtex_citation(data: dict[str, Any]) -> str:
    """Formats metadata into BibTeX citation style."""
    first, last, _ = _parse_author(data.get("author_name", ""))
    _, year, month, day = _parse_date(data.get("date", ""))
    
    author_str = f"{last}, {first}" if last else first
    title = data.get("title", "Untitled")
    inst = data.get("author_institution", "")
    code = data.get("archive_code", "")
    platform = data.get("platform_name", "NATO Archive Obsidian")
    
    safe_id = safe_identifier(code)
    url = data.get("url", f"https://nato-obsidian.kky.zcu.cz/{safe_id}")
    urldate = data.get("url_date", "")

    note_parts = [p for p in [inst, code, platform] if p]
    note = ", ".join(note_parts)

    safe_id = safe_identifier(code)
    lines = [f"@misc{{{safe_id},"]
    lines.append(f"  author = {{{author_str}}},")
    lines.append(f"  title = {{{title}}},")
    if year:
        lines.append(f"  year = {{{year}}},")
    if month:
        lines.append(f"  month = {{{month}}},")
    if day:
        lines.append(f"  day = {{{day}}},")
    if note:
        lines.append(f"  note = {{{note}}},")
    if url:
        lines.append(f"  url = {{{url}}},")
    if urldate:
        lines.append(f"  urldate = {{{urldate}}}")
    
    return "\n".join(lines) + "\n}"


def generate_citation_callout(data: dict[str, Any]) -> str:
    """Generates the full Obsidian callout with all citation styles."""
    chicago = format_chicago_citation(data)
    harvard = format_harvard_citation(data)
    bibtex = format_bibtex_citation(data)

    callout_content = (
        "**Chicago**:\n"
        "```\n"
        f"{chicago}\n"
        "```\n\n"
        "**Harvard**:\n"
        "```\n"
        f"{harvard}\n"
        "```\n\n"
        "**BibTeX**:\n"
        "```\n"
        f"{bibtex}\n"
        "```"
    )

    return format_as_callout(callout_content, title="", callout_type="citing this document")


def safe_read_text(path: Path) -> str:
    """Reads text from a file with UTF-8 encoding and error replacement."""
    return path.read_text(encoding="utf-8", errors="replace")


def mirror_file(src: Path, dst: Path) -> None:
    """Mirrors a file from src to dst using hardlinks if possible, else copying."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(src, dst)
    except (OSError, FileExistsError):
        # Fallback to copy if hardlink fails or target already exists
        shutil.copy2(src, dst)
