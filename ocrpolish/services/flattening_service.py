from typing import Any


class FlatteningService:
    """Service for linearizing a nested topic hierarchy into a flat list."""

    def flatten(self, hierarchy: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Flattens a nested Category/Topic hierarchy.

        Args:
            hierarchy: The nested hierarchy dictionary.

        Returns:
            A list of flattened topic definitions with 'id', 'description', 
            'positive_samples', and 'negative_samples'.
        """
        flat_topics = []
        for cat in hierarchy.get("categories", []):
            cat_name = cat.get("category", "Unknown")
            for topic in cat.get("topics", []):
                topic_name = topic.get("topic", "Unknown")
                flat_topic = {
                    "id": f"{cat_name}/{topic_name}",
                    "description": topic.get("description", ""),
                }

                # Process positive samples
                pos = topic.get("positive_samples")
                if pos:
                    samples = [s.strip() for s in pos.split("\n") if s.strip()]
                    flat_topic["positive_samples"] = samples

                # Process negative samples
                neg = topic.get("negative_samples")
                if neg:
                    samples = [s.strip() for s in neg.split("\n") if s.strip()]
                    flat_topic["negative_samples"] = samples

                flat_topics.append(flat_topic)

        return flat_topics
