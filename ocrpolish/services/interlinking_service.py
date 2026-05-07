import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

@dataclass
class VaultDocument:
    path: Path
    vault_relative_path: str
    archive_code: str
    normalized_code: str
    language: str
    references: list[str] = field(default_factory=list)

class InterlinkingService:
    """Service for interlinking documents in an Obsidian vault."""
    
    def __init__(self, vault_dir: Path):
        self.vault_dir = vault_dir
        self.code_map: dict[str, dict[str, str]] = {} # normalized_code -> {lang: relative_path}

    @staticmethod
    def normalize_code(code: str) -> str:
        """Removes all whitespace and treats / and - as equivalent."""
        if not code:
            return ""
        # Remove whitespace
        code = re.sub(r"\s+", "", str(code))
        # Treat / and - as same for lookup
        return code.replace("-", "/")

    def resolve_link(self, target_code: str, source_lang: str) -> str | None:
        """
        Resolves a target_code to a vault-relative path using language priority.
        Priority: source_lang -> English -> Any other available language.
        """
        normalized = self.normalize_code(target_code)
        variants = self.code_map.get(normalized)
        if not variants:
            return None
            
        # 1. Current language
        if source_lang in variants:
            return variants[source_lang]
            
        # 2. English fallback
        if "English" in variants:
            return variants["English"]
            
        # 3. Any available
        return next(iter(variants.values()))

    def discover(self):
        """First pass: build the archive code map by scanning all Markdown files."""
        self.code_map = {}
        for md_file in self.vault_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                # Simple frontmatter extraction
                match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
                if not match:
                    continue
                    
                frontmatter = yaml.safe_load(match.group(1))
                if not frontmatter:
                    continue
                    
                code = frontmatter.get("archive_code")
                lang = frontmatter.get("language")
                
                if code and lang:
                    norm_code = self.normalize_code(code)
                    # Use only filename as requested
                    filename = md_file.name
                    
                    if norm_code not in self.code_map:
                        self.code_map[norm_code] = {}
                    self.code_map[norm_code][lang] = filename
            except Exception:
                # Silently skip files that can't be parsed
                continue

    def get_boundary_regex(self, code: str) -> str:
        """
        Generates a regex for matching a code at a prefix boundary.
        Boundary: start of string or non-alphanumeric character.
        Following char must be non-alphanumeric or end of string.
        """
        escaped = re.escape(code)
        # Prefix boundary: not preceded by alphanumeric
        # Suffix boundary: not followed by alphanumeric
        return rf"(?<![a-zA-Z0-9]){escaped}(?![a-zA-Z0-9])"

    def interlink_metadata(
        self,
        content: str,
        source_lang: str,
        current_filename: str | None = None,
        discovered_codes: list[str] | None = None,
    ) -> str:
        """
        Processes the Metadata callout table in the content.
        Updates 'references' with links, merges discovered codes, and adds language_versions.
        """
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
        archive_code = None
        for row in table_body.split("\n"):
            code_match = re.match(r"^\s*> \| ≡&nbsp;archive_code: \| (.*?) \|", row)
            if code_match:
                archive_code = code_match.group(1).strip()
                break
        
        lang_versions_row = ""
        if archive_code:
            norm_code = self.normalize_code(archive_code)
            variants = self.code_map.get(norm_code, {})
            # language_versions links to OTHER files with the same code
            other_variants = {lang: p for lang, p in variants.items() if p != current_filename}
            
            if other_variants:
                links = [f"[{lang}]({p})" for lang, p in sorted(other_variants.items())]
                lang_versions_row = f"> | ≡&nbsp;language_versions: | {'<br>'.join(links)} |"

        # 2. Process rows
        rows = table_body.split("\n")
        new_rows = []
        
        # We'll handle the references row specially to ensure ordering
        found_ref_row = False
        
        for row in rows:
            # Skip existing language_versions row if present (idempotency)
            if "language_versions:" in row:
                continue
                
            # Match references row
            ref_match = re.match(r"^(\s*> \| ☰&nbsp;references: \| )(.*)( \|)$", row)
            if ref_match:
                found_ref_row = True
                prefix, values_str, suffix = ref_match.groups()
                # Use <br> as requested by the user
                sep = "<br>"
                parts = re.split(r"<br>|,", values_str) # Support splitting both for migration
                
                existing_codes = []
                for part in parts:
                    stripped_part = part.strip()
                    if not stripped_part:
                        continue
                    # Extract code if it's already a link
                    link_match = re.match(r"^\[(.*?)\]\(.*?\)$", stripped_part)
                    code = link_match.group(1) if link_match else stripped_part
                    if code not in existing_codes:
                        existing_codes.append(code)
                
                # Merge with discovered_codes (from body)
                # discovered_codes are in order of occurrence.
                body_codes = discovered_codes or []
                final_codes = []
                
                # First: Add all from body in order of appearance
                for c in body_codes:
                    if c not in final_codes:
                        final_codes.append(c)
                
                # Second: Add existing ones that were NOT in body (silent references)
                for c in existing_codes:
                    if c not in final_codes:
                        final_codes.append(c)
                
                # Format back with links
                new_parts = []
                for code in final_codes:
                    link_path = self.resolve_link(code, source_lang)
                    if link_path and link_path != current_filename:
                        new_parts.append(f"[{code}]({link_path})")
                    else:
                        new_parts.append(code)
                
                new_rows.append(f"{prefix}{sep.join(new_parts)}{suffix}")
                continue
                
            new_rows.append(row)
            
            # Insert language_versions row after language row
            if "language:" in row and lang_versions_row:
                new_rows.append(lang_versions_row)
        
        # If no reference row was found but we have discovered codes, add it!
        if not found_ref_row and discovered_codes:
            new_parts = []
            for code in discovered_codes:
                link_path = self.resolve_link(code, source_lang)
                if link_path and link_path != current_filename:
                    new_parts.append(f"[{code}]({link_path})")
                else:
                    new_parts.append(code)
            
            # Find a good place to insert (after language_versions or intent)
            insert_idx = len(new_rows)
            for i, r in enumerate(new_rows):
                if "language_versions:" in r or "language:" in r or "intent:" in r:
                    insert_idx = i + 1
            
            ref_row = f"> | ☰&nbsp;references: | {'<br>'.join(new_parts)} |"
            new_rows.insert(insert_idx, ref_row)
            
        new_table_body = "\n".join(new_rows)
        return content[:match.start()] + header + new_table_body + content[match.end():]

    def interlink_body(self, content: str, source_lang: str, current_filename: str | None = None) -> tuple[str, list[str]]:
        """
        Processes the Markdown body.
        Converts occurrences of known archive codes to Markdown links.
        Skips lines containing 'archive_code:'.
        Ensures idempotency by not matching inside existing links.
        Prevents linking a document to itself.
        Returns (new_content, ordered_list_of_codes_found).
        """
        # Sort codes by length descending to ensure longest match priority
        sorted_codes = sorted(self.code_map.keys(), key=len, reverse=True)
        if not sorted_codes:
            return content, []

        # Build a single regex to match either any existing link or any archive code
        # For codes, we allow / and - interchangeably by replacing / in normalized code with [/-]
        def make_flexible(c):
            return re.escape(c).replace("/", "[/-]")
            
        codes_regex_parts = [make_flexible(c) for c in sorted_codes]
        codes_pattern = "|".join(codes_regex_parts)
        
        combined_pattern = re.compile(
            rf"(\[\[.*?\]\]|\[.*?\]\(.*?\))|(?<![a-zA-Z0-9\[])({codes_pattern})(?![a-zA-Z0-9\]])"
        )

        found_codes = []
        lines = content.split("\n")
        new_lines = []

        for line in lines:
            if "archive_code:" in line:
                new_lines.append(line)
                continue

            def replace_match(m):
                if m.group(1):
                    # Existing link - try to identify if it's one of our codes
                    link_text = m.group(1)
                    for c in sorted_codes:
                        if c in link_text: # Loose match for codes inside links
                            if c not in found_codes:
                                found_codes.append(c)
                            break
                    return link_text

                # Archive code
                code = m.group(2)
                if code not in found_codes:
                    found_codes.append(code)
                    
                link_path = self.resolve_link(code, source_lang)
                if link_path and link_path != current_filename:
                    return f"[{code}]({link_path})"
                return code

            processed_line = combined_pattern.sub(replace_match, line)
            new_lines.append(processed_line)

        return "\n".join(new_lines), found_codes

    def interlink_all(self, dry_run: bool = False, verbose: bool = False):
        """Second pass: perform in-place interlinking on all files."""
        updated_count = 0
        for md_file in self.vault_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                
                # 1. Separate frontmatter from body to protect it
                fm_match = re.match(r"^(---\s*\n.*?\n---\s*\n)(.*)$", content, re.DOTALL)
                if fm_match:
                    frontmatter_part = fm_match.group(1)
                    body_part = fm_match.group(2)
                    
                    # Extract source language for logic
                    fm_data = yaml.safe_load(re.match(r"^---\s*\n(.*?)\n---\s*\n", frontmatter_part, re.DOTALL).group(1))
                    source_lang = fm_data.get("language", "English")
                else:
                    frontmatter_part = ""
                    body_part = content
                    source_lang = "English"
                
                # 2. Interlink Body FIRST to discover all references and their order
                new_body, discovered_codes = self.interlink_body(body_part, source_lang, md_file.name)
                
                # 3. Interlink Metadata callout with discovered codes
                new_body = self.interlink_metadata(new_body, source_lang, md_file.name, discovered_codes)
                
                new_content = frontmatter_part + new_body
                
                if new_content != content:
                    rel_path = md_file.relative_to(self.vault_dir)
                    if verbose or dry_run:
                        action = "[DRY-RUN] Would update" if dry_run else "Updating"
                        logger.info(f"{action}: {rel_path}")
                    
                    if not dry_run:
                        md_file.write_text(new_content, encoding="utf-8")
                    updated_count += 1
                        
            except Exception as e:
                logger.error(f"Error processing {md_file}: {e}")
                continue
        
        msg = f"Interlinking complete. {updated_count} files modified"
        if dry_run:
            msg += " (dry-run)"
        logger.info(msg)
