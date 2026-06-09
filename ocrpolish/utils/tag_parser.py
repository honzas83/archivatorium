import logging
import re
from pathlib import Path

from ocrpolish.models.metadata import CanonicalTags
from ocrpolish.utils.nlp import normalize_tag_component

logger = logging.getLogger(__name__)

# Matches tags starting with #Entities/, #Topics/, or #Tags/
# Allows spaces inside components for OCR/LLM error resilience (e.g. 'United States'),
# but space-separated components must start with an uppercase letter or number
# to avoid matching sentence words like 'and'.
TAG_PATTERN = re.compile(
    r"#(?:Entities|Topics|Tags)/[a-zA-Z0-9_/-]+(?:\s+[A-Z0-9][a-zA-Z0-9_-]*|/[a-zA-Z0-9_/-]+)*"
)

# Constants to avoid magic values
MIN_ENTITY_COMPONENTS = 2
STANDARD_ENTITY_COMPONENTS = 3
CITY_ENTITY_COMPONENTS = 4
MIN_TOPIC_COMPONENTS = 2
MIN_CONCEPTUAL_TAG_COMPONENTS = 2


class CanonicalTagParser:
    """Parses, normalizes, and validates canonical tags in Markdown files."""

    def parse_text(self, text: str, file_path: Path | None = None) -> CanonicalTags:
        """Parses a block of text and returns a CanonicalTags model."""
        tags = CanonicalTags()
        if not text:
            return tags

        # Find all raw hashtags matching the pattern
        raw_matches = TAG_PATTERN.findall(text)
        for raw_match in raw_matches:
            # 1. Strip leading #
            clean_tag = raw_match.lstrip("#")

            # 2. Split into components
            parts = clean_tag.split("/")

            # 3. Normalize each component
            normalized_parts = [normalize_tag_component(p) for p in parts]

            # 4. Check for empty components after normalization
            if any(not p for p in normalized_parts):
                logger.warning(
                    f"Malformed generated tag ignored: {raw_match} (Contains empty component)"
                )
                continue

            prefix = normalized_parts[0]

            # 5. Route by prefix to keep code simple
            if prefix == "Entities":
                self._parse_entity(raw_match, normalized_parts, tags)
            elif prefix == "Topics":
                self._parse_topic(raw_match, normalized_parts, tags)
            elif prefix == "Tags":
                self._parse_conceptual(raw_match, normalized_parts, tags)

        return tags

    def _parse_entity(
        self, raw_match: str, normalized_parts: list[str], tags: CanonicalTags
    ) -> None:
        """Parses and validates #Entities/... tags."""
        if len(normalized_parts) < MIN_ENTITY_COMPONENTS:
            logger.warning(f"Malformed generated tag ignored: {raw_match} (Missing entity type)")
            return

        etype = normalized_parts[1]
        valid_types = {"State", "Org", "City", "Person"}
        matching_type = next((t for t in valid_types if t.lower() == etype.lower()), None)

        if not matching_type:
            logger.warning(
                f"Malformed generated tag ignored: {raw_match} (Unsupported entity type: {etype})"
            )
            return

        if matching_type in {"State", "Org", "Person"}:
            if len(normalized_parts) != STANDARD_ENTITY_COMPONENTS:
                logger.warning(
                    f"Malformed generated tag ignored: {raw_match} "
                    f"({matching_type} tag must have format #Entities/{matching_type}/<Name>)"
                )
                return
            val = normalized_parts[2]
            tags.entities[matching_type].add(val.lower())

        elif matching_type == "City":
            if len(normalized_parts) != CITY_ENTITY_COMPONENTS:
                logger.warning(
                    f"Malformed generated tag ignored: {raw_match} "
                    f"(City tag must have format #Entities/City/<State>/<City>)"
                )
                return
            state = normalized_parts[2]
            city = normalized_parts[3]
            tags.entities["City"].add(f"{state.lower()}/{city.lower()}")

        # Reconstruct raw path with preserved casing (normalized type casing)
        normalized_parts[1] = matching_type
        raw_path = "/".join(normalized_parts)
        tags.raw_paths.add(raw_path)

    def _parse_topic(
        self, raw_match: str, normalized_parts: list[str], tags: CanonicalTags
    ) -> None:
        """Parses and validates #Topics/... tags."""
        if len(normalized_parts) < MIN_TOPIC_COMPONENTS:
            logger.warning(
                f"Malformed generated tag ignored: {raw_match} "
                f"(Topic tag must have format #Topics/<taxonomy-path>)"
            )
            return

        val = "/".join([p.lower() for p in normalized_parts[1:]])
        tags.topics.add(val)

        raw_path = "/".join(normalized_parts)
        tags.raw_paths.add(raw_path)

    def _parse_conceptual(
        self, raw_match: str, normalized_parts: list[str], tags: CanonicalTags
    ) -> None:
        """Parses and validates #Tags/... tags."""
        if len(normalized_parts) < MIN_CONCEPTUAL_TAG_COMPONENTS:
            logger.warning(
                f"Malformed generated tag ignored: {raw_match} "
                f"(Conceptual tag must have format #Tags/<tag-path>)"
            )
            return

        val = "/".join(normalized_parts[1:])
        tags.conceptual_tags.add(val.lower())

        raw_path = "/".join(normalized_parts)
        tags.raw_paths.add(raw_path)
