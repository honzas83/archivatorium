import logging
from pathlib import Path
from typing import Any

import yaml

from ocrpolish.models.topics import CategorySelectionSchema, TopicAssignment, TopicSelectionSchema
from ocrpolish.services.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class TopicExtractor:
    def __init__(self, ollama_client: OllamaClient, hierarchy_path: Path):
        self.client = ollama_client
        self.hierarchy_path = hierarchy_path
        self.hierarchy = self._load_hierarchy()

    def _load_hierarchy(self) -> dict[str, Any]:
        """Loads the topic hierarchy from the YAML file."""
        try:
            with open(self.hierarchy_path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load topic hierarchy from {self.hierarchy_path}: {e}")
            raise

    def _generate_category_prompt(self, first_chunk: str) -> str:
        """Generates the prompt for the first step: category selection."""
        categories_info = []
        for cat in self.hierarchy.get("categories", []):
            name = cat.get("category")
            desc = cat.get("description", "")
            categories_info.append(f"- {name}: {desc}")

        categories_list = "\n".join(categories_info)

        return (
            "Document Excerpt:\n\n"
            f"{first_chunk}\n\n"
            "Based on the content above, select all applicable high-level categories "
            "from the following list:\n\n"
            f"{categories_list}\n\n"
            "Respond with the list of selected category names."
        )

    def _generate_topic_prompt(
        self, first_chunk: str, selected_categories: list[str]
    ) -> str:
        """Generates the prompt for the second step: topic selection within categories."""
        topics_info = []
        # Filter hierarchy to only include selected categories
        relevant_cats = [
            cat for cat in self.hierarchy.get("categories", [])
            if cat.get("category") in selected_categories
        ]

        for cat in relevant_cats:
            cat_name = cat.get("category")
            for topic in cat.get("topics", []):
                name = topic.get("topic")
                desc = topic.get("description", "")
                pos = topic.get("positive_anchor", "")
                neg = topic.get("negative_anchor", "")
                
                info = f"Category: {cat_name}\nTopic: {name}\nDescription: {desc}"
                if pos:
                    info += f"\nPositive Anchor: {pos}"
                if neg:
                    info += f"\nNegative Anchor: {neg}"
                topics_info.append(info)

        topics_list = "\n\n".join(topics_info)

        return (
            "Document Excerpt:\n\n"
            f"{first_chunk}\n\n"
            "You have previously selected the following categories: "
            f"{', '.join(selected_categories)}.\n\n"
            "Now, select the most important specific topics within these categories "
            "that apply to the document. \n\n"
            "CRITICAL INSTRUCTIONS FOR TOPIC SELECTION:\n"
            "1. Select AT MOST 3 topics. However, you DO NOT need to use all 3 slots. "
            "Quality and precision are more important than quantity.\n"
            "2. Be particularly selective for shorter documents (e.g., less than 3 pages). "
            "Only assign a topic if it is a major theme of the document.\n"
            "3. If only one or two topics truly fit, only return those.\n\n"
            "CRITICAL INSTRUCTIONS FOR REASONING:\n"
            "1. For each selected topic, provide a specific reason why it was selected based on "
            "concrete facts in the text.\n"
            "2. DO NOT provide generic, circular, or obvious reasons (e.g., 'the meeting was in 1974', "
            "'it involves strategic relationships', or 'the context involves NATO').\n"
            "3. Identify unique elements, specific named entities, or particular policy shifts "
            "that justify the assignment.\n\n"
            f"{topics_list}\n\n"
            "Respond with a list of category-topic assignments and their corresponding specific reasons."
        )

    def extract_topics(self, first_chunk: str) -> list[TopicAssignment]:
        """Performs the two-step topic extraction process."""
        # Step 1: Category Selection
        category_prompt = self._generate_category_prompt(first_chunk)
        try:
            category_selection = self.client.extract_structured(
                category_prompt, CategorySelectionSchema
            )
            selected_cats = category_selection.selected_categories
        except Exception as e:
            logger.error(f"Step 1 (Category Selection) failed: {e}")
            return []

        if not selected_cats:
            logger.info("No categories selected by the LLM.")
            return []

        # Step 2: Topic Selection
        topic_prompt = self._generate_topic_prompt(first_chunk, selected_cats)
        try:
            topic_selection = self.client.extract_structured(
                topic_prompt, TopicSelectionSchema
            )
            return topic_selection.assignments
        except Exception as e:
            logger.error(f"Step 2 (Topic Selection) failed: {e}")
            return []
