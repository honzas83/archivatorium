from typing import Any

from archivatorium.utils.nlp import normalize_tag_component


class TaxonomyValidationError(ValueError):
    """Raised when a topic hierarchy cannot be used safely for classification."""


class FlatteningService:
    """Validate and linearize a nested topic hierarchy into classifier-ready records."""

    _V2_POLICY_FIELDS = (
        "substantive_subject_rule",
        "omission_rule",
        "insufficient_evidence_rule",
    )

    def flatten(self, hierarchy: dict[str, Any]) -> list[dict[str, Any]]:
        """Return validated Category/Topic definitions with complete category context."""
        if not isinstance(hierarchy, dict):
            raise TaxonomyValidationError("Taxonomy root must be a mapping.")

        self._validate_v2_policy(hierarchy)
        categories = hierarchy.get("categories")
        if not isinstance(categories, list) or not categories:
            raise TaxonomyValidationError("Taxonomy categories must be a non-empty list.")

        flat_topics: list[dict[str, Any]] = []
        known_paths: set[str] = set()
        for category_index, category in enumerate(categories):
            flat_topics.extend(self._flatten_category(category, category_index, known_paths))
        return flat_topics

    def _validate_v2_policy(self, hierarchy: dict[str, Any]) -> None:
        version = hierarchy.get("schema_version")
        if version is None:
            return
        if version != 2:
            raise TaxonomyValidationError("schema_version must be 2 when present.")

        policy = hierarchy.get("classification_policy")
        if not isinstance(policy, dict):
            raise TaxonomyValidationError("Schema v2 requires a classification_policy mapping.")
        for field in self._V2_POLICY_FIELDS:
            self._require_text(policy.get(field), f"classification_policy.{field}")

    def _flatten_category(
        self,
        category: Any,
        category_index: int,
        known_paths: set[str],
    ) -> list[dict[str, Any]]:
        location = f"categories[{category_index}]"
        if not isinstance(category, dict):
            raise TaxonomyValidationError(f"{location} must be a mapping.")

        category_name = self._require_component(category.get("category"), f"{location}.category")
        category_description = self._require_text(
            category.get("description"), f"{location}.description"
        )
        topics = category.get("topics")
        if not isinstance(topics, list) or not topics:
            raise TaxonomyValidationError(f"{location}.topics must be a non-empty list.")

        return [
            self._flatten_topic(
                topic,
                topic_index,
                location,
                category_name,
                category_description,
                known_paths,
            )
            for topic_index, topic in enumerate(topics)
        ]

    def _flatten_topic(
        self,
        topic: Any,
        topic_index: int,
        category_location: str,
        category_name: str,
        category_description: str,
        known_paths: set[str],
    ) -> dict[str, Any]:
        location = f"{category_location}.topics[{topic_index}]"
        if not isinstance(topic, dict):
            raise TaxonomyValidationError(f"{location} must be a mapping.")

        topic_name = self._require_component(topic.get("topic"), f"{location}.topic")
        topic_description = self._require_text(topic.get("description"), f"{location}.description")
        positive_samples = self._parse_samples(
            topic.get("positive_samples"), f"{location}.positive_samples"
        )
        negative_samples = self._parse_samples(
            topic.get("negative_samples"), f"{location}.negative_samples"
        )
        topic_id = f"{category_name}/{topic_name}"
        normalized_id = self._normalize_path(topic_id)
        if normalized_id in known_paths:
            raise TaxonomyValidationError(
                f"Taxonomy contains duplicate normalized topic path: {normalized_id}"
            )
        known_paths.add(normalized_id)

        return {
            "id": topic_id,
            "category": category_name,
            "category_description": category_description,
            "description": topic_description,
            "positive_samples": positive_samples,
            "negative_samples": negative_samples,
        }

    def _require_component(self, value: Any, location: str) -> str:
        text = self._require_text(value, location)
        if "/" in text:
            raise TaxonomyValidationError(f"{location} must not contain '/'.")
        if not normalize_tag_component(text):
            raise TaxonomyValidationError(f"{location} becomes empty after normalization.")
        return text

    @staticmethod
    def _require_text(value: Any, location: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise TaxonomyValidationError(f"{location} must be a non-empty string.")
        return value.strip()

    def _parse_samples(self, value: Any, location: str) -> list[str]:
        text = self._require_text(value, location)
        samples = [sample.strip() for sample in text.splitlines() if sample.strip()]
        if not samples:
            raise TaxonomyValidationError(f"{location} must contain a non-empty sample.")
        return samples

    @staticmethod
    def _normalize_path(topic_id: str) -> str:
        return "/".join(normalize_tag_component(part) for part in topic_id.split("/"))
