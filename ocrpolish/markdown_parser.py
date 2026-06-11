import re
from typing import Dict


class MarkdownPageParser:
    """Parses page contents from generated markdown files using page headers."""

    # Matches: --- \n\n # Page X \n\n or similar variants, capturing page number.
    PAGE_HEADER_PATTERN = re.compile(r"(?:^|\n)---\s*\n+# Page (\d+)\s*\n+", re.MULTILINE)

    @classmethod
    def parse_pages(cls, content: str) -> Dict[int, str]:
        """
        Parses a markdown string and returns a mapping of page number to content.
        """
        pages: Dict[int, str] = {}
        matches = list(cls.PAGE_HEADER_PATTERN.finditer(content))

        if not matches:
            # If no page headers are found, we can't parse pages individually.
            # Return empty mapping.
            return pages

        for i, match in enumerate(matches):
            page_num = int(match.group(1))
            start_idx = match.end()

            # The content for this page ends at the start of the next match
            if i + 1 < len(matches):
                end_idx = matches[i + 1].start()
            else:
                end_idx = len(content)

            page_content = content[start_idx:end_idx].strip()
            pages[page_num] = page_content

        return pages
