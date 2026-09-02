from pathlib import Path
from unittest.mock import MagicMock

from archivatorium.models.metadata import TopicResult, WindowTaggingResult
from archivatorium.services.tagging_service import TaggingService


def test_substantive_policy_and_empty_topic_flow(
    hierarchy_file: Path, useful_tags_file: Path
) -> None:
    client = MagicMock()
    windowing = MagicMock()
    service = TaggingService(
        client,
        windowing,
        hierarchy_file,
        useful_tags_file,
        context_limit=1000,
    )
    client.extract_structured.side_effect = [
        WindowTaggingResult(
            conceptual_tags=["Nuclear-Planning"],
            topic_tags=[
                TopicResult(
                    topic="Defence Policy/Nuclear Planning",
                    reason="The proposal substantively defines nuclear planning procedures.",
                )
            ],
        ),
        WindowTaggingResult(conceptual_tags=[]),
    ]

    substantive = service.extract_tags(
        "The proposal substantively defines nuclear planning procedures."
    )
    administrative = service.extract_tags(
        "This document is incorporated into the initial document and cancelled."
    )

    assert [topic.topic for topic in substantive.topic_tags] == ["Defence-Policy/Nuclear-Planning"]
    assert administrative.topic_tags == []
    prompts = [call.args[0] for call in client.extract_structured.call_args_list]
    assert all("classification_policy:" in prompt for prompt in prompts)
    assert all("Prefer omission" in prompt for prompt in prompts)
    assert client.extract_structured.call_count == 2
