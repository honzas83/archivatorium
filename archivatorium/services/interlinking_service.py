import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from archivatorium.models.metadata import CanonicalTags
from archivatorium.utils.metadata import (
    is_generated_document_markdown,
    parse_frontmatter,
    safe_identifier,
    stringify_frontmatter,
)
from archivatorium.utils.tag_parser import CanonicalTagParser

logger = logging.getLogger(__name__)


@dataclass
class VaultDocument:
    path: Path
    vault_relative_path: str
    body: str
    frontmatter: dict[str, Any] = field(default_factory=dict)
    archive_code: str = ""
    language: str = "English"
    raw_references: list[str] = field(default_factory=list)
    canonical_tags: CanonicalTags = field(default_factory=CanonicalTags)


class InterlinkingService:
    """Service for interlinking documents in an Obsidian vault."""

    def __init__(self, vault_dir: Path, unifications_path: Path | None = None):
        self.vault_dir = vault_dir
        self.code_map: dict[str, dict[str, str]] = {}  # normalized_code -> {lang: relative_path}
        self.bibtex_map: dict[str, dict[str, str]] = {}  # bibtex_key -> {lang: relative_path}
        self.bib_to_norm: dict[str, str] = {}  # bibtex_key -> normalized_code
        self.unifications: list[dict[str, str]] = self._load_unifications(unifications_path)
        self.expansion_map: dict[str, list[str]] = self._build_expansion_map()
        self.documents: list[VaultDocument] = []

    def clean_citekey(self, citekey: str) -> str:
        """
        Cleans a potentially broken citekey that contains markdown link brackets, e.g.:
        '[NPG-D-73-6](NPG-D(73)6_FRE.md)_ENG' -> 'NPG-D-73-6_ENG'
        """
        if not citekey:
            return ""
        # Handle nested parentheses in URLs and optional suffixes like -COR1
        match = re.match(r"^\[([^\]]*)\]\((?:[^()]|\([^()]*\))*\)(-[a-zA-Z0-9\-]+|)(_[A-Z]{3})$", citekey)
        if match:
            text, suffix_cor, suffix_lang = match.groups()
            return f"{text}{suffix_cor}{suffix_lang}"
        return citekey

    def clean_citation_callout(self, citation_text: str) -> str:
        """
        Cleans any markdown links that got incorrectly inserted into the citation block.
        """
        if not citation_text:
            return ""
        # Match nested parentheses in URLs and optional suffixes like -COR1 using suffix group
        return re.sub(r'\[([^\]]*)\]\((?:[^()]|\([^()]*\))*\)(-[a-zA-Z0-9\-]+|)(_[A-Z]{3})', r'\1\2\3', citation_text)

    def infer_archive_code(self, filename: str) -> str:
        """
        Infers archive_code from the filename, e.g.:
        NPG-D(73)6_ENG.md -> NPG/D(73)6
        NPG-WP(73)1-COR1_ENG.md -> NPG/WP(73)1-COR1
        """
        stem = Path(filename).stem
        # Strip language suffix like _ENG, _FRE, _BIL
        stem = re.sub(r'_(ENG|FRE|BIL)$', '', stem, flags=re.IGNORECASE)
        # Replace the first dash with a slash if it's like NPG-D, NPG-WP, NPG-SG, NPG-STUDY
        for prefix in ["NPG-D", "NPG-WP", "NPG-SG", "NPG-STUDY", "MC-D", "MC-WP"]:
            if stem.startswith(prefix):
                return stem.replace("-", "/", 1)
        # Fallback to replacing the first dash if it's alphanumeric on both sides
        match = re.match(r"^([A-Z]+)-([A-Z0-9]+)\b", stem, re.IGNORECASE)
        if match:
            return stem.replace("-", "/", 1)
        return stem

    def split_body_parts(self, body_content: str) -> tuple[str, str, str, str]:
        """
        Splits body content into:
        1. metadata_callout (str)
        2. abstract_callout (str)
        3. main_body (str)
        4. citation_callout (str)
        """
        lines = body_content.splitlines(keepends=True)
        metadata_lines = []
        abstract_lines = []
        main_body_lines = []
        citation_lines = []

        current_section = "main_body"

        i = 0
        n = len(lines)
        while i < n:
            line = lines[i]
            stripped = line.strip()
            if stripped.startswith("> [!"):
                header_lower = stripped.lower()
                if "[!info]" in header_lower and "metadata" in header_lower:
                    current_section = "metadata"
                elif "[!metadata]" in header_lower:
                    current_section = "metadata"
                elif "[!abstract]" in header_lower:
                    current_section = "abstract"
                elif "[!citing" in header_lower:
                    current_section = "citation"
                else:
                    current_section = "main_body"

            if current_section in ("metadata", "abstract", "citation"):
                if not stripped.startswith(">"):
                    current_section = "main_body"

            if current_section == "metadata":
                metadata_lines.append(line)
            elif current_section == "abstract":
                abstract_lines.append(line)
            elif current_section == "citation":
                citation_lines.append(line)
            else:
                main_body_lines.append(line)

            i += 1

        return (
            "".join(metadata_lines),
            "".join(abstract_lines),
            "".join(main_body_lines),
            "".join(citation_lines),
        )

    def _load_unifications(self, custom_path: Path | None = None) -> list[dict[str, str]]:
        """Loads unification rules from topics/unifications.yaml or a custom path."""
        unif_path = custom_path or Path("topics/unifications.yaml")
        if not unif_path.exists():
            if custom_path:
                logger.warning(f"Custom unification rules not found at {unif_path}")
            else:
                logger.debug(f"Default unification rules not found at {unif_path}")
            return []

        try:
            with open(unif_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if isinstance(data, dict):
                    unif = data.get("unifications", [])
                    if isinstance(unif, list):
                        return unif
                return []
        except Exception as e:
            logger.warning(f"Could not load unification rules: {e}")
            return []

    def _build_expansion_map(self) -> dict[str, list[str]]:
        """
        Builds a map from canonical replacement to a list of variant patterns.
        Used to expand search regexes in body text.
        """
        expansion: dict[str, list[str]] = {}
        for rule in self.unifications:
            replacement = rule.get("replacement")
            pattern = rule.get("pattern")
            if replacement and pattern:
                if replacement not in expansion:
                    expansion[replacement] = []
                expansion[replacement].append(pattern)
        return expansion

    def normalize_code(self, code: str) -> str:
        """
        Removes all whitespace and treats / and - as equivalent.
        Applies global unification rules first.
        """
        if not code:
            return ""

        # 1. Apply global unification rules (regex)
        normalized = str(code)
        for rule in self.unifications:
            pattern = rule.get("pattern")
            replacement = rule.get("replacement")
            if pattern and replacement is not None:
                try:
                    normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
                except Exception as e:
                    logger.warning(f"Failed to apply unification rule '{pattern}': {e}")

        # 2. Standard normalization: Remove whitespace
        normalized = re.sub(r"\s+", "", normalized)
        # 3. Standard normalization: Treat / and - as same for lookup
        return normalized.replace("-", "/")

    def resolve_link(self, target_code: str, source_lang: str) -> str | None:
        """
        Resolves a target_code to a vault-relative path using language priority.
        Priority:
        1. Exact match in source_lang
        2. BibTeX-style fuzzy match in source_lang
        3. Exact match in English
        4. BibTeX-style fuzzy match in English
        5. Exact match in any lang
        6. BibTeX-style fuzzy match in any lang
        """
        normalized = self.normalize_code(target_code)
        bib = safe_identifier(target_code)

        exact_variants = self.code_map.get(normalized, {})
        bib_variants = self.bibtex_map.get(bib, {})

        # 1 & 2: Source language
        if source_lang in exact_variants:
            return exact_variants[source_lang]
        if source_lang in bib_variants:
            return bib_variants[source_lang]

        # 3 & 4: English fallback
        if "English" in exact_variants:
            return exact_variants["English"]
        if "English" in bib_variants:
            return bib_variants["English"]

        # 5 & 6: Any other language
        if exact_variants:
            # Sort for stable selection
            best_lang = sorted(exact_variants.keys())[0]
            return exact_variants[best_lang]
        if bib_variants:
            # Sort for stable selection
            best_lang = sorted(bib_variants.keys())[0]
            return bib_variants[best_lang]

        return None

    @staticmethod
    def _format_document_link_target(target_path: str) -> str:
        """Format generated document links as filename-only Markdown targets."""
        return Path(target_path).name

    def discover(self) -> None:
        """First pass: build the archive code maps by scanning all Markdown files, excluding index files, etc."""
        self.code_map = {}
        self.bibtex_map = {}
        self.bib_to_norm = {}
        self.documents = []

        # Sort files for deterministic behavior (handles duplicate codes consistently)
        files = sorted(list(self.vault_dir.rglob("*.md")))
        tag_parser = CanonicalTagParser()

        for md_file in files:
            if md_file.name.startswith("."):
                continue
            if not is_generated_document_markdown(md_file, vault_root=self.vault_dir):
                continue

            try:
                content = md_file.read_text(encoding="utf-8")
                # Parse frontmatter and body
                metadata, body = parse_frontmatter(content)

                # Clean citekey if it got broken
                citekey = metadata.get("citekey", "")
                if citekey:
                    metadata["citekey"] = self.clean_citekey(citekey)

                # Default values if missing
                code = metadata.get("archive_code", "")
                if not code:
                    code = self.infer_archive_code(md_file.name)
                    metadata["archive_code"] = code

                lang = metadata.get("language", "English")
                if not lang:
                    lang = "English"

                # Parse canonical tags using CanonicalTagParser
                canonical_tags = tag_parser.parse_text(content, file_path=md_file)

                # References list
                raw_refs = metadata.get("references", [])
                if not isinstance(raw_refs, list):
                    raw_refs = [raw_refs] if raw_refs else []

                doc = VaultDocument(
                    path=md_file,
                    vault_relative_path=str(md_file.relative_to(self.vault_dir)),
                    body=body,
                    frontmatter=metadata,
                    archive_code=code,
                    language=lang,
                    raw_references=raw_refs,
                    canonical_tags=canonical_tags,
                )
                self.documents.append(doc)

                if code:
                    norm_code = self.normalize_code(code)
                    bib_code = safe_identifier(code)
                    rel_path = doc.vault_relative_path

                    # Add to exact map
                    if norm_code not in self.code_map:
                        self.code_map[norm_code] = {}
                    self.code_map[norm_code][lang] = rel_path

                    # Add to BibTeX map as fuzzy fallback
                    if bib_code not in self.bibtex_map:
                        self.bibtex_map[bib_code] = {}
                        # Map BibTeX key to the first normalized code that produces it
                        self.bib_to_norm[bib_code] = norm_code

                    # Only add if not already present for this lang
                    if lang not in self.bibtex_map[bib_code]:
                        self.bibtex_map[bib_code][lang] = rel_path
            except Exception as e:
                logger.warning(f"Failed to scan/parse {md_file}: {e}")
                continue

    def get_boundary_regex(self, code: str) -> str:
        """
        Generates a regex for matching a code at a prefix boundary.
        Boundary: start of string or non-alphanumeric character.
        Following char must be non-alphanumeric or end of string.
        """
        escaped = re.escape(code)
        return rf"(?<![a-zA-Z0-9]){escaped}(?![a-zA-Z0-9])"

    def interlink_metadata(
        self,
        content: str,
        source_lang: str,
        current_relative_path: str | None = None,
        discovered_codes: list[str] | None = None,
        current_filename: str | None = None,
        own_archive_code: str | None = None,
    ) -> str:
        """
        Processes the Metadata callout table in the content.
        Updates 'references' with links, merges discovered codes, and adds language_versions.
        """
        # Alias for backward compatibility in unit tests
        cur_path = current_relative_path or current_filename

        # Regex to find the [!info] Metadata callout block
        callout_pattern = re.compile(
            r"(> \[!info\] Metadata.*?\n)(.*?)(?=\n\n|\n[^>]|$)", re.DOTALL
        )

        match = callout_pattern.search(content)
        if not match:
            return content

        header = match.group(1)
        table_body = match.group(2)

        # 1. Resolve language versions for this document
        archive_code = own_archive_code
        # Support both bolded and non-bolded labels
        archive_code_re = re.compile(r"^\s*> \| ≡&nbsp;(?:\*\*)?archive_code(?:\*\*)?: \| (.*?) \|")
        for row in table_body.split("\n"):
            code_match = archive_code_re.match(row)
            if code_match:
                archive_code = code_match.group(1).strip()
                # Remove bold markers from extracted code if LLM added them
                archive_code = archive_code.replace("**", "")
                break

        # 2. Process rows
        rows = table_body.split("\n")

        # If we have own_archive_code but it's not present in rows, insert it
        has_archive_code_row = any(archive_code_re.match(r) for r in rows)
        if own_archive_code and not has_archive_code_row:
            insert_idx = len(rows)
            for i, r in enumerate(rows):
                if "language:" in r or "citekey:" in r:
                    insert_idx = i
                    break
            archive_code_row = f"> | ≡&nbsp;archive_code: | {own_archive_code} |"
            rows.insert(insert_idx, archive_code_row)
            archive_code = own_archive_code

        lang_versions_row = ""
        if archive_code:
            norm_code = self.normalize_code(archive_code)
            variants = self.code_map.get(norm_code, {})
            # language_versions links to OTHER files with the same code
            other_variants = {lang: p for lang, p in variants.items() if p != cur_path}

            if other_variants:
                links = [
                    f"[{lang}]({self._format_document_link_target(p)})"
                    for lang, p in sorted(other_variants.items())
                ]
                # Non-bold as requested
                lang_versions_row = f"> | ≡&nbsp;language_versions: | {'<br>'.join(links)} |"

        new_rows = []

        # We'll handle the references row specially to ensure ordering
        found_ref_row = False

        # Precise regex for detecting language and references rows (supporting optional bolding)
        lang_re = re.compile(r"^\s*> \| ≡&nbsp;(?:\*\*)?language(?:\*\*)?: \|")
        lang_versions_re = re.compile(r"^\s*> \| ≡&nbsp;(?:\*\*)?language_versions(?:\*\*)?: \|")
        refs_re = re.compile(r"^(\s*> \| ☰&nbsp;(?:\*\*)?references(?:\*\*)?: \| )(.*)( \|)$")

        for row in rows:
            # Skip existing language_versions row if present (idempotency)
            if lang_versions_re.match(row):
                continue

            # Clean broken citekey if found in the row
            if "citekey:" in row:
                row_match = re.match(r"^(\s*> \| ≡&nbsp;(?:\*\*)?citekey(?:\*\*)?: \| )(.*)( \|)$", row)
                if row_match:
                    prefix, citekey_val, suffix = row_match.groups()
                    clean_val = self.clean_citekey(citekey_val.strip())
                    row = f"{prefix}{clean_val}{suffix}"

            # Match references row
            ref_match = refs_re.match(row)
            if ref_match:
                found_ref_row = True
                prefix, values_str, suffix = ref_match.groups()
                # Use <br> as requested by the user
                sep = "<br>"
                parts = re.split(r"<br>|,", values_str)  # Support splitting both for migration

                existing_codes = []
                for part in parts:
                    stripped_part = part.strip()
                    if not stripped_part:
                        continue
                    # Extract code if it's already a link
                    link_match = re.match(r"^\[(.*?)\]\(.*?\)$", stripped_part)
                    raw_code = link_match.group(1) if link_match else stripped_part
                    # Canonicalize
                    canonical = self.bib_to_norm.get(raw_code, raw_code)
                    if canonical not in existing_codes:
                        existing_codes.append(canonical)

                # Merge with discovered_codes (from body)
                body_codes = discovered_codes or []
                final_codes = []

                # Normalize own archive_code for strict comparison (using BibTeX-style key)
                own_code_bib = safe_identifier(archive_code) if archive_code else None

                # First: Add all from body in order of appearance
                for c in body_codes:
                    if c not in final_codes:
                        # Skip if it's the document's own archive_code (BibTeX-style fuzzy check)
                        if own_code_bib and safe_identifier(c) == own_code_bib:
                            continue
                        final_codes.append(c)

                # Second: Add existing ones that were NOT in body (silent references)
                for c in existing_codes:
                    if c not in final_codes:
                        # Skip if it's the document's own archive_code
                        if own_code_bib and safe_identifier(c) == own_code_bib:
                            continue
                        final_codes.append(c)

                # Format back with links
                new_parts = []
                for code in final_codes:
                    link_path = self.resolve_link(code, source_lang)
                    if link_path and link_path != cur_path:
                        target = self._format_document_link_target(link_path)
                        new_parts.append(f"[{code}]({target})")
                    else:
                        new_parts.append(code)

                new_rows.append(f"{prefix}{sep.join(new_parts)}{suffix}")
                continue

            new_rows.append(row)

            # Insert language_versions row after language row
            if lang_re.match(row) and lang_versions_row:
                new_rows.append(lang_versions_row)

        # If no reference row was found but we have discovered codes, add it!
        if not found_ref_row and discovered_codes:
            new_parts = []
            own_code_bib = safe_identifier(archive_code) if archive_code else None

            for code in discovered_codes:
                # Skip if it's the document's own archive_code (BibTeX-style fuzzy check)
                if own_code_bib and safe_identifier(code) == own_code_bib:
                    continue

                link_path = self.resolve_link(code, source_lang)
                if link_path and link_path != cur_path:
                    target = self._format_document_link_target(link_path)
                    new_parts.append(f"[{code}]({target})")
                else:
                    new_parts.append(code)

            if new_parts:
                # Find a good place to insert (after language_versions or intent)
                insert_idx = len(new_rows)
                for i, r in enumerate(new_rows):
                    if "language_versions:" in r or "language:" in r or "intent:" in r:
                        insert_idx = i + 1

                ref_row = f"> | ☰&nbsp;references: | {'<br>'.join(new_parts)} |"
                new_rows.insert(insert_idx, ref_row)

        new_table_body = "\n".join(new_rows)
        return content[: match.start()] + header + new_table_body + content[match.end() :]

    def interlink_body(
        self,
        content: str,
        source_lang: str,
        current_relative_path: str | None = None,
        own_archive_code: str | None = None,
        force: bool = False,
        current_filename: str | None = None,
    ) -> tuple[str, list[str]]:
        """
        Processes the Markdown body.
        Converts occurrences of known archive codes to Markdown links.
        Skips lines containing 'archive_code:'.
        Ensures idempotency by not matching inside existing links (unless force is True).
        Prevents linking a document to itself.
        Returns (new_content, ordered_list_of_codes_found).
        """
        # Alias for backward compatibility in unit tests
        cur_path = current_relative_path or current_filename

        # Sort codes by length descending to ensure longest match priority
        # Include both exact codes and BibTeX-style keys
        all_search_keys = set(self.code_map.keys()) | set(self.bibtex_map.keys())
        sorted_codes = sorted(all_search_keys, key=len, reverse=True)
        if not sorted_codes:
            return content, []

        # Build a single regex to match either any existing link or any archive code
        # For codes, we allow /, -, and spaces interchangeably and optionally
        def make_flexible(c: str) -> str:
            # 1. Expand canonical parts to include variants from expansion_map
            expanded = c
            placeholders: dict[str, str] = {}
            for canonical, variants in sorted(
                self.expansion_map.items(), key=lambda x: len(x[0]), reverse=True
            ):
                if canonical in expanded:
                    esc_canonical = re.escape(canonical)
                    all_variants = [esc_canonical] + variants
                    group = f"(?:{'|'.join(all_variants)})"

                    ph = f"___GROUP{len(placeholders)}___"
                    placeholders[ph] = group
                    expanded = expanded.replace(canonical, ph)

            # 2. re.escape handles parentheses and other special chars
            s = re.escape(expanded)

            # 3. Replace escaped or unescaped / and - with [/ \-]*
            s = re.sub(r"\\/|/|\\-|-", r"[/ \\-]*", s)
            s = s.replace(r"\(", r"[/ \\-]*\(").replace(r"\)", r"\)[/ \\-]*")

            # 4. Restore placeholders
            for ph, group in placeholders.items():
                s = s.replace(re.escape(ph), group)

            # 5. Collapse multiple identical patterns to keep it clean
            while "[/ \\-]*[/ \\-]*" in s:
                s = s.replace("[/ \\-]*[/ \\-]*", "[/ \\-]*")
            return s

        codes_regex_parts = [make_flexible(c) for c in sorted_codes]
        codes_pattern = "|".join(codes_regex_parts)

        # Single-pass regex to avoid re-linking already linked text.
        combined_pattern = re.compile(
            rf"(\[\[.*?\]\]|\[[^\]]*\]\((?:[^()]|\([^()]*\))*\))|(?<![a-zA-Z0-9\[])({codes_pattern})(?![a-zA-Z0-9\]/])"
        )

        found_codes = []
        lines = content.split("\n")
        new_lines = []

        own_code_bib = safe_identifier(own_archive_code) if own_archive_code else None

        for line in lines:
            if "archive_code:" in line:
                new_lines.append(line)
                continue

            def process_code(code_text: str, display_text: str | None = None) -> str:
                if display_text is None:
                    display_text = code_text
                bib = safe_identifier(code_text)

                # Self-linking prevention
                if own_code_bib and bib == own_code_bib:
                    return display_text

                canonical = self.bib_to_norm.get(bib, self.normalize_code(code_text))
                if canonical not in found_codes:
                    found_codes.append(canonical)

                link_path = self.resolve_link(code_text, source_lang)
                if link_path and link_path != cur_path:
                    target = self._format_document_link_target(link_path)
                    return f"[{display_text}]({target})"
                return display_text

            def replace_match(m: re.Match[str]) -> str:
                # 1. Existing link (Wikilink or Markdown)
                if m.group(1):
                    link_text = m.group(1)
                    if force:
                        # Markdown link: [text](path)
                        md_link = re.match(r"^\[(.*?)\]\((.*?)\)$", link_text)
                        if md_link:
                            text = md_link.group(1)
                            if safe_identifier(text) in self.bib_to_norm:
                                return process_code(text)

                        # Wikilink: [[target]] or [[target|display]]
                        wiki_link = re.match(r"^\[\[(.*?)(?:\|(.*?))?\]\]$", link_text)
                        if wiki_link:
                            target, display = wiki_link.groups()
                            text = display if display else target
                            if safe_identifier(text) in self.bib_to_norm:
                                return process_code(text)
                            if safe_identifier(target) in self.bib_to_norm:
                                return process_code(target, display_text=text)

                    # Extract canonical codes but don't modify the link text
                    link_bib = safe_identifier(link_text)
                    for c in sorted_codes:
                        bib = safe_identifier(c)
                        if bib and bib in link_bib:
                            canonical = self.bib_to_norm.get(bib, c)
                            if canonical not in found_codes:
                                found_codes.append(canonical)
                            break
                    return link_text

                # 2. Raw archive code
                return process_code(m.group(2))

            processed_line = combined_pattern.sub(replace_match, line)
            new_lines.append(processed_line)

        return "\n".join(new_lines), found_codes

    def interlink_all(
        self, dry_run: bool = False, verbose: bool = False, force: bool = False
    ) -> None:
        """Second pass: perform in-place interlinking on all files, then reparse updated ones."""
        updated_count = 0
        from archivatorium.utils.metadata import parse_frontmatter
        from archivatorium.utils.tag_parser import CanonicalTagParser

        tag_parser = CanonicalTagParser()

        for doc in self.documents:
            md_file = doc.path
            try:
                content = md_file.read_text(encoding="utf-8")

                # 1. Separate frontmatter from body to protect it
                fm_match = re.match(r"^(---\s*\n.*?\n---\s*\n)(.*)$", content, re.DOTALL)
                if fm_match:
                    frontmatter_part = stringify_frontmatter(doc.frontmatter)
                    body_part = fm_match.group(2)
                    source_lang = doc.language
                else:
                    frontmatter_part = ""
                    body_part = content
                    source_lang = "English"

                # 2. Split body part to protect metadata and citation callouts
                metadata_callout, abstract_callout, main_body, citation_callout = self.split_body_parts(body_part)

                # 3. Interlink abstract and main body (protecting metadata and citation callouts)
                new_abstract, desc_codes_abstract = self.interlink_body(
                    abstract_callout, source_lang, doc.vault_relative_path, doc.archive_code, force=force
                )
                new_main, desc_codes_body = self.interlink_body(
                    main_body, source_lang, doc.vault_relative_path, doc.archive_code, force=force
                )

                # Combine discovered codes maintaining order
                discovered_codes = []
                for c in desc_codes_abstract + desc_codes_body:
                    if c not in discovered_codes:
                        discovered_codes.append(c)

                # 4. Interlink Metadata callout with discovered codes
                updated_metadata_callout = self.interlink_metadata(
                    metadata_callout, source_lang, doc.vault_relative_path, discovered_codes,
                    own_archive_code=doc.archive_code
                )

                # 5. Clean citation callout (in case it is already broken)
                cleaned_citation_callout = self.clean_citation_callout(citation_callout)

                # Assemble everything back
                new_body_parts = []
                if updated_metadata_callout.strip():
                    new_body_parts.append(updated_metadata_callout.strip())
                if new_abstract.strip():
                    new_body_parts.append(new_abstract.strip())
                if new_main.strip():
                    new_body_parts.append(new_main.strip())

                new_body = "\n\n".join(new_body_parts)
                if not new_body.endswith("\n\n") and not new_body.endswith("\n"):
                    new_body += "\n\n"
                elif new_body.endswith("\n") and not new_body.endswith("\n\n"):
                    new_body += "\n"

                if cleaned_citation_callout.strip():
                    new_body += cleaned_citation_callout.strip() + "\n"

                new_content = frontmatter_part + new_body

                if new_content != content:
                    rel_path = doc.vault_relative_path
                    if verbose or dry_run:
                        action = "[DRY-RUN] Would update" if dry_run else "Updating"
                        logger.info(f"{action}: {rel_path}")

                    if not dry_run:
                        md_file.write_text(new_content, encoding="utf-8")

                        # Reparse the document to update in-memory record
                        reparsed_content = new_content
                        metadata, body = parse_frontmatter(reparsed_content)
                        doc.body = body
                        doc.frontmatter = metadata
                        doc.archive_code = metadata.get("archive_code", "")
                        doc.language = metadata.get("language", "English") or "English"

                        raw_refs = metadata.get("references", [])
                        if not isinstance(raw_refs, list):
                            raw_refs = [raw_refs] if raw_refs else []
                        doc.raw_references = raw_refs

                        doc.canonical_tags = tag_parser.parse_text(
                            reparsed_content, file_path=md_file
                        )

                    updated_count += 1

            except Exception as e:
                logger.error(f"Error processing {md_file}: {e}")
                continue

        msg = f"Interlinking complete. {updated_count} files modified"
        if dry_run:
            msg += " (dry-run)"
        logger.info(msg)
