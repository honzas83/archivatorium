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
        """Removes all whitespace from the archive code."""
        if not code:
            return ""
        return re.sub(r"\s+", "", str(code))

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
                    rel_path = str(md_file.relative_to(self.vault_dir))
                    
                    if norm_code not in self.code_map:
                        self.code_map[norm_code] = {}
                    self.code_map[norm_code][lang] = rel_path
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

    def interlink_metadata(self, content: str, source_lang: str) -> str:
        """
        Processes the Metadata callout table in the content.
        Updates 'references' with links and adds language_versions.
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
            other_langs = {lang: p for lang, p in variants.items() if lang != source_lang}
            
            if other_langs:
                links = [f"[{lang}]({p})" for lang, p in sorted(other_langs.items())]
                lang_versions_row = f"> | ≡&nbsp;language_versions: | {'<br>'.join(links)} |"

        # 2. Process rows
        rows = table_body.split("\n")
        new_rows = []
        
        for row in rows:
            # Skip existing language_versions row if present (idempotency)
            if "language_versions:" in row:
                continue
                
            # Match references row
            ref_match = re.match(r"^(\s*> \| ☰&nbsp;references: \| )(.*)( \|)$", row)
            if ref_match:
                prefix, values_str, suffix = ref_match.groups()
                sep = "<br>" if "<br>" in values_str else ","
                parts = values_str.split(sep)
                
                new_parts = []
                for part in parts:
                    stripped_part = part.strip()
                    if not stripped_part:
                        continue
                    link_match = re.match(r"^\[(.*?)\]\(.*?\)$", stripped_part)
                    code_to_resolve = link_match.group(1) if link_match else stripped_part
                    link_path = self.resolve_link(code_to_resolve, source_lang)
                    if link_path:
                        new_parts.append(f"[{code_to_resolve}]({link_path})")
                    else:
                        new_parts.append(code_to_resolve)
                
                new_rows.append(f"{prefix}{sep.join(new_parts)}{suffix}")
                continue
                
            new_rows.append(row)
            
            # Insert language_versions row after language row
            if "language:" in row and lang_versions_row:
                new_rows.append(lang_versions_row)
            
        new_table_body = "\n".join(new_rows)
        return content[:match.start()] + header + new_table_body + content[match.end():]

    def interlink_body(self, content: str, source_lang: str) -> str:
        """
        Processes the Markdown body.
        Converts occurrences of known archive codes to Markdown links.
        """
        # Sort codes by length descending to ensure longest match priority
        sorted_codes = sorted(self.code_map.keys(), key=len, reverse=True)
        
        for code in sorted_codes:
            link_path = self.resolve_link(code, source_lang)
            if not link_path:
                continue
                
            escaped_code = re.escape(code)
            # Match existing link: [CODE](...)
            existing_link_pattern = rf"\[{escaped_code}\]\(.*?\)"
            # Match raw code at boundaries, avoiding already linked ones (heuristic)
            raw_code_pattern = rf"(?<![a-zA-Z0-9\[]){escaped_code}(?![a-zA-Z0-9\]])"
            
            combined_pattern = f"({existing_link_pattern})|({raw_code_pattern})"
            
            content = re.sub(combined_pattern, f"[{code}]({link_path})", content)
            
        return content

    def interlink_all(self, dry_run: bool = False, verbose: bool = False):
        """Second pass: perform in-place interlinking on all files."""
        updated_count = 0
        for md_file in self.vault_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                
                # 1. Extract source language from frontmatter
                fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
                if not fm_match:
                    continue
                
                frontmatter = yaml.safe_load(fm_match.group(1))
                if not frontmatter:
                    continue
                    
                source_lang = frontmatter.get("language", "English")
                
                # 2. Interlink Metadata callout
                new_content = self.interlink_metadata(content, source_lang)
                
                # 3. Interlink Body
                new_content = self.interlink_body(new_content, source_lang)
                
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
