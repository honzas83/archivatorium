import os
import re
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from ocrpolish.data_model import PageMetadata
from ocrpolish.utils.nlp import normalize_tag_component


GENERATED_SUPPORT_FILENAMES = {
    "metadata_index.xlsx",
}

GENERATED_SUPPORT_DIR_PARTS = {
    "templates",
    "template",
}


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


def prefix_tag(tag: str, root_prefix: str | None) -> str:
    """
    Adds a root prefix to a tag if not already present.
    If root_prefix is None, no prefix is added.
    Ensures normalization and returns the tag with a leading '#'.
    """
    # Normalize the incoming tag (no hash)
    norm_tag = normalize_tag_component(tag)

    if not norm_tag:
        return ""

    if not root_prefix:
        return f"#{norm_tag}"

    # Standardize root prefix (normalized, no hash)
    norm_root = normalize_tag_component(root_prefix)

    if norm_tag.startswith(f"{norm_root}/") or norm_tag == norm_root:
        return f"#{norm_tag}"

    return f"#{norm_root}/{norm_tag}"


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
    Extracts the total page count by counting occurrences of '# Page [Number]'.
    """
    matches = re.findall(r"^# Page \d+", content, re.MULTILINE)
    return len(matches) if matches else None


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


def _parse_author(author_name: str) -> tuple[str, str, str] | None:
    if not author_name:
        return None
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
    author_info = _parse_author(data.get("author_name", ""))
    date_chicago, _, _, _ = _parse_date(data.get("date", ""))

    inst = data.get("author_institution", "")
    if author_info:
        first, last, _ = author_info
        author_str = f"{first}, {last}" if last else first
    else:
        author_str = inst or "[Unknown Author]"

    title = data.get("title", "Untitled")
    code = data.get("archive_code", "")
    platform = data.get("platform_name", "NATO Archive Obsidian")

    citekey = data.get("citekey")
    if not citekey:
        citekey = safe_identifier(code)
    url = data.get("url", f"https://nato-obsidian.kky.zcu.cz/{citekey}")
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
    author_info = _parse_author(data.get("author_name", ""))
    _, year, _, _ = _parse_date(data.get("date", ""))

    inst = data.get("author_institution", "")
    if author_info:
        _, last, initials = author_info
        author_str = f"{last}, {initials}" if last else author_info[0]
    else:
        author_str = inst or "[Unknown Author]"

    title = data.get("title", "Untitled")
    code = data.get("archive_code", "")
    platform = data.get("platform_name", "NATO Archive Obsidian")

    citekey = data.get("citekey")
    if not citekey:
        citekey = safe_identifier(code)
    url = data.get("url", f"https://nato-obsidian.kky.zcu.cz/{citekey}")
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


def format_metadata_table(metadata: dict[str, Any]) -> str:
    """
    Formats key metadata fields into a markdown table with specific icons.
    Icons: ≡&nbsp; (text), №&nbsp; (pages), 🗓&nbsp; (date), 🔗&nbsp; (source), ☰&nbsp; (references)
    """
    # Mapping based on MUSTR_metadata_table2.md
    mapping = [
        ("≡&nbsp;**title**:", metadata.get("title", "Untitled")),
        ("≡&nbsp;summary:", metadata.get("summary", "")),
        ("№&nbsp;**pages**:", str(metadata.get("pages", ""))),
        ("🔗&nbsp;source:", metadata.get("source", "")),
        ("≡&nbsp;sender:", metadata.get("sender", "")),
        ("≡&nbsp;recipient:", metadata.get("recipient", "")),
        ("≡&nbsp;intent:", metadata.get("intent", "")),
        ("≡&nbsp;author_name:", metadata.get("author_name", "")),
        ("≡&nbsp;author_institution:", metadata.get("author_institution", "")),
        ("🗓&nbsp;**date**:", metadata.get("date", "")),
        ("≡&nbsp;archive_code:", metadata.get("archive_code", "")),
        ("≡&nbsp;citekey:", metadata.get("citekey", "")),
        ("≡&nbsp;**language**:", metadata.get("language", "")),
        ("≡&nbsp;location_city:", metadata.get("location_city", "")),
        ("≡&nbsp;location_state:", metadata.get("location_state", "")),
        ("☰&nbsp;references:", metadata.get("references", "")),
        ("☰&nbsp;references (derived):", metadata.get("references (derived)", "")),
        ("≡&nbsp;language versions (derived):", metadata.get("language_versions (derived)", "")),
    ]

    table_lines = []
    first = True
    for field, value in mapping:
        if value and str(value).strip() and value != "[]":
            # Format list values as separate lines using <br> for table cells
            if isinstance(value, list):
                value = "<br>".join([str(v) for v in value])

            # Ensure value is single-line for table compatibility
            clean_value = str(value).replace("\n", " ").strip()

            # Bold the value only if the field label is bolded
            if "**" in field:
                clean_value = f"**{clean_value}**"

            table_lines.append(f"| {field} | {clean_value} |")
            if first:
                table_lines.append("| --- | --- |")
                first = False

    if not table_lines:
        return ""

    return "\n".join(table_lines)


def format_bibtex_citation(data: dict[str, Any]) -> str:
    """Formats metadata into BibTeX citation style."""
    author_info = _parse_author(data.get("author_name", ""))
    date = data.get("date", "")

    inst = data.get("author_institution", "")
    if author_info:
        first, last, _ = author_info
        author_str = f"{last}, {first}" if last else first
    else:
        author_str = inst or "[Unknown Author]"

    title = data.get("title", "Untitled")
    code = data.get("archive_code", "")
    platform = data.get("platform_name", "NATO Archive Obsidian")

    citekey = data.get("citekey")
    if not citekey:
        citekey = safe_identifier(code)
    url = data.get("url", f"https://nato-obsidian.kky.zcu.cz/{citekey}")
    urldate = data.get("url_date", "")

    note_parts = [p for p in [inst, code, platform] if p]
    note = ", ".join(note_parts)

    lines = [f"@misc{{{citekey},"]
    lines.append(f"  author = {{{author_str}}},")
    lines.append(f"  title = {{{title}}},")
    if date:
        lines.append(f"  date = {{{date}}},")
    if note:
        lines.append(f"  note = {{{note}}},")
    if url:
        lines.append(f"  url = {{{url}}},")
    if urldate:
        lines.append(f"  urldate = {{{urldate}}}")

    return "\n".join(lines).rstrip(",") + "\n}"


def format_coins_span(data: dict[str, Any]) -> str:
    """Generates a COinS HTML span for browser extensions like Zotero."""
    import urllib.parse
    
    author_info = _parse_author(data.get("author_name", ""))
    date_str = data.get("date", "")
    
    year = ""
    if date_str:
        try:
            from datetime import datetime
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            year = str(dt.year)
        except ValueError:
            year = date_str[:4]
            
    title = data.get("title", "Untitled")
    publisher = data.get("author_institution", "NATO Archive Obsidian")
    code = data.get("archive_code", "")
    citekey = data.get("citekey") or safe_identifier(code)
    url = data.get("url", f"https://nato-obsidian.kky.zcu.cz/{citekey}")

    coins_data = {
        "ctx_ver": "Z39.88-2004",
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:dc",
        "rft.type": "document",
        "rft.title": title,
        "rft.publisher": publisher,
        "rft.identifier": [url, citekey],
    }
    
    if year:
        coins_data["rft.date"] = year
        
    if author_info:
        first, last, _ = author_info
        if last:
            coins_data["rft.creator"] = f"{last}, {first}"
        else:
            coins_data["rft.creator"] = first
            
    language = data.get("language", "")
    if language:
        coins_data["rft.language"] = language

    encoded_data = urllib.parse.urlencode(coins_data, doseq=True).replace("&", "&amp;")
    
    return f'<span class="Z3988" title="{encoded_data}"></span>'


def generate_citation_callout(data: dict[str, Any]) -> str:
    """Generates the full Obsidian callout with all citation styles."""
    chicago = format_chicago_citation(data)
    harvard = format_harvard_citation(data)
    bibtex = format_bibtex_citation(data)
    coins = format_coins_span(data)

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
        "```\n"
        f"{coins}"
    )

    return format_as_callout(callout_content, title="", callout_type="citing this document")


def strip_generated_sections(content: str) -> str:
    """
    Strips YAML frontmatter, Metadata callouts, Abstract callouts, and Citation callouts
    to return only the clean source Markdown text.
    """
    # 1. Strip YAML frontmatter
    _, body = parse_frontmatter(content)
    body = body.lstrip()

    # 2. Strip callout blocks line-by-line
    lines = body.splitlines()
    cleaned_lines = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("> [!"):
            callout_header = stripped.lower()
            if (
                ("[!info]" in callout_header and "metadata" in callout_header)
                or ("[!metadata]" in callout_header)
                or ("[!abstract]" in callout_header)
                or ("[!citing this document]" in callout_header)
            ):
                # Skip callout block lines
                i += 1
                while i < n and (lines[i].strip().startswith(">") or lines[i].strip() == ""):
                    if not lines[i].strip().startswith(">"):
                        break
                    i += 1
                continue
        cleaned_lines.append(line)
        i += 1

    return "\n".join(cleaned_lines).strip()


def generate_citekey(
    output_file: Path,
    mode: str = "stem",
    vault_root: Path | None = None,
    output_dir: Path | None = None,
) -> str:
    """
    Generates a normalized citekey from the output file.
    - stem mode: filename stem.
    - path mode: full vault-relative path of the output file without the '.md' suffix.
    """
    if mode == "path":
        rel_path = None
        if vault_root:
            try:
                rel_path = output_file.resolve().relative_to(vault_root.resolve())
            except ValueError:
                pass
        if rel_path is None and output_dir:
            try:
                rel_path = output_file.resolve().relative_to(output_dir.resolve())
            except ValueError:
                pass

        if rel_path:
            path_str = rel_path.with_suffix("").as_posix()
            path_str = path_str.replace("/", ":")
            return safe_identifier(path_str)

    return safe_identifier(output_file.stem)


def reconcile_metadata(
    existing_meta: dict[str, Any],
    newly_extracted: dict[str, Any],
) -> dict[str, Any]:
    """
    Reconciles existing user-supplied metadata with newly extracted metadata.
    """
    canonical_fields = {
        "title",
        "summary",
        "abstract",
        "pages",
        "source",
        "sender",
        "recipient",
        "intent",
        "author_name",
        "author_institution",
        "date",
        "archive_code",
        "citekey",
        "language",
        "location_city",
        "location_state",
        "references",
    }

    reconciled: dict[str, Any] = {}

    # 1. Preserve all custom fields
    for k, v in existing_meta.items():
        if k not in canonical_fields:
            reconciled[k] = v

    # 2. Reconcile canonical fields
    overwrite_fields = {"summary", "pages", "source", "citekey", "abstract"}
    for field in overwrite_fields:
        if field in newly_extracted:
            reconciled[field] = newly_extracted[field]
        elif field in existing_meta:
            reconciled[field] = existing_meta[field]

    preserve_fields = {
        "title",
        "sender",
        "recipient",
        "intent",
        "author_name",
        "author_institution",
        "date",
        "archive_code",
        "language",
        "location_city",
        "location_state",
    }
    for field in preserve_fields:
        existing_val = existing_meta.get(field)
        new_val = newly_extracted.get(field)
        if existing_val not in (None, "", [], {}):
            reconciled[field] = existing_val
        elif new_val not in (None, "", [], {}):
            reconciled[field] = new_val

    # Special merge for references
    existing_refs = existing_meta.get("references")
    new_refs = newly_extracted.get("references")

    merged_refs_set: set[str] = set()
    if isinstance(existing_refs, list):
        merged_refs_set.update(str(r).strip() for r in existing_refs if r)
    elif isinstance(existing_refs, str) and existing_refs.strip():
        merged_refs_set.add(existing_refs.strip())

    if isinstance(new_refs, list):
        merged_refs_set.update(str(r).strip() for r in new_refs if r)
    elif isinstance(new_refs, str) and new_refs.strip():
        merged_refs_set.add(new_refs.strip())

    if merged_refs_set:
        reconciled["references"] = sorted(list(merged_refs_set))

    return reconciled


def safe_read_text(path: Path) -> str:
    """Reads text from a file with UTF-8 encoding and error replacement."""
    return path.read_text(encoding="utf-8", errors="replace")


def generated_document_exclusion_reason(path: Path, vault_root: Path | None = None) -> str | None:
    """Return why a vault file is not an eligible generated document, or None."""
    if path.suffix.lower() != ".md":
        return "not-markdown"
    if path.name.endswith(".filtered.md"):
        return "filtered-sidecar"
    if path.name.startswith("Index - "):
        return "index-page"
    if path.name.lower() == "index.md":
        return "support-index"
    if path.name in GENERATED_SUPPORT_FILENAMES:
        return "support-file"

    parts = path.parts
    if vault_root is not None:
        try:
            parts = path.resolve().relative_to(vault_root.resolve()).parts
        except ValueError:
            parts = path.parts

    for part in parts:
        lower_part = part.lower()
        if part.startswith("."):
            return "hidden-system-folder"
        if lower_part in GENERATED_SUPPORT_DIR_PARTS or "template" in lower_part:
            return "template-path"

    return None


def is_generated_document_markdown(path: Path, vault_root: Path | None = None) -> bool:
    """Return True when path is an eligible generated document Markdown output."""
    return generated_document_exclusion_reason(path, vault_root=vault_root) is None


def mirror_file(src: Path, dst: Path) -> None:
    """Mirrors a file from src to dst using hardlinks if possible, else copying."""
    if not src.exists():
        return

    dst.parent.mkdir(parents=True, exist_ok=True)

    if dst.exists():
        try:
            if os.path.samefile(src, dst):
                return
        except OSError:
            pass

    try:
        os.link(src, dst)
    except (OSError, FileExistsError):
        # Fallback to copy if hardlink fails or target already exists
        # shutil.copy2 handles SameFileError internally in newer Python versions
        # but we check explicitly above to be safe and avoid unnecessary work
        shutil.copy2(src, dst)
