import unittest
from pathlib import Path
from unittest.mock import MagicMock

from ocrpolish.models.topics import (
    CategorySelectionSchema,
    TopicAssignment,
    TopicSelectionSchema,
)
from ocrpolish.services.topics_service import TopicExtractor


class TestTopicExtractor(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        # Create a temporary hierarchy for testing
        self.hierarchy_path = Path("tests/test_hierarchy.yaml")
        self.hierarchy_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.hierarchy_path, "w", encoding="utf-8") as f:
            f.write(
                """
categories:
  - category: "Category A"
    description: "Desc A"
    topics:
      - topic: "Topic A1"
        description: "Desc A1"
  - category: "Category B"
    description: "Desc B"
    topics:
      - topic: "Topic B1"
        description: "Desc B1"
"""
            )
        self.extractor = TopicExtractor(self.mock_client, self.hierarchy_path)

    def tearDown(self):
        if self.hierarchy_path.exists():
            self.hierarchy_path.unlink()

    def test_extract_topics_success(self):
        # Mock step 1 response
        self.mock_client.extract_structured.side_effect = [
            CategorySelectionSchema(selected_categories=["Category A"]),
            TopicSelectionSchema(
                assignments=[TopicAssignment(category="Category A", topic="Topic A1", reason="Strong match")]
            ),
        ]

        results = self.extractor.extract_topics("Some text chunk")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].category, "Category A")
        self.assertEqual(results[0].topic, "Topic A1")
        self.assertEqual(self.mock_client.extract_structured.call_count, 2)

    def test_extract_topics_no_categories(self):
        # Mock step 1 response with no categories
        self.mock_client.extract_structured.return_value = CategorySelectionSchema(
            selected_categories=[]
        )

        results = self.extractor.extract_topics("Some text chunk")

        self.assertEqual(len(results), 0)
        self.assertEqual(self.mock_client.extract_structured.call_count, 1)

    def test_extract_topics_failure_step_1(self):
        # Mock step 1 failure
        self.mock_client.extract_structured.side_effect = Exception("Ollama error")

        results = self.extractor.extract_topics("Some text chunk")

        self.assertEqual(len(results), 0)
        self.assertEqual(self.mock_client.extract_structured.call_count, 1)
