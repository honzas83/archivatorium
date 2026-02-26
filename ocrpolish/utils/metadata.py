import re
from collections import Counter

from ocrpolish.data_model import PageMetadata


class FileMetadataAnalyzer:
    """Analyzes metadata patterns across all pages of a single file."""

    def __init__(self, threshold: float = 0.8):
        self.threshold = threshold
        self.header_counts: Counter[str] = Counter()
        self.footer_counts: Counter[str] = Counter()
        self.total_pages = 0
        self.identified_header: str | None = None
        self.identified_footer: str | None = None

    def add_page(self, metadata: PageMetadata) -> None:
        """Add page metadata to the analysis."""
        self.total_pages += 1
        # Use sets to count each candidate at most once per page
        for candidate in set(metadata.header_candidates):
            self.header_counts[candidate] += 1
        for candidate in set(metadata.footer_candidates):
            self.footer_counts[candidate] += 1

    def analyze(self) -> None:
        """Identify headers/footers that meet the threshold."""
        if self.total_pages <= 1:
            return

        # Find most frequent candidates that meet the threshold
        for counts, attribute in [
            (self.header_counts, "identified_header"),
            (self.footer_counts, "identified_footer"),
        ]:
            if not counts:
                continue

            # Get the most common
            most_common_str, count = counts.most_common(1)[0]
            if count / self.total_pages >= self.threshold:
                setattr(self, attribute, most_common_str)


def extract_page_number(text: str) -> int | None:
    """
    Extract a page number from a string if it matches '- X -', '-X-', '~ X ~', or '~X~'.
    """
    stripped = text.strip()
    # Matches '- X -', '-X-', '~ X ~', or '~X~' where X is a sequence of digits
    match = re.match(r"^[~-]\s*(\d+)\s*[~-]$", stripped)
    if match:
        return int(match.group(1))
    return None
