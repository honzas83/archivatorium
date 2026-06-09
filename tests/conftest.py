from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from ocrpolish.models.metadata import AggregatedTaggingResult, MetadataSchema, TopicResult
from tests.unit.test_ollama_client import create_mock_ollama_response


@pytest.fixture
def hierarchy_file(tmp_path: Path) -> Path:
    path = tmp_path / "hierarchy.yaml"
    path.write_text(
        """
categories:
  - category: Defence Policy
    description: Defence policy matters
    topics:
      - topic: Nuclear Planning
        description: Nuclear planning documents
        positive_samples: nuclear planning group
        negative_samples: routine agenda
""".lstrip(),
        encoding="utf-8",
    )
    return path


@pytest.fixture
def useful_tags_file(tmp_path: Path) -> Path:
    path = tmp_path / "useful_tags.yaml"
    path.write_text(
        """
useful_tags:
  - Nuclear Planning
  - NATO
  - Ministerial Guidance
""".lstrip(),
        encoding="utf-8",
    )
    return path


@pytest.fixture
def metadata_response_factory() -> Callable[..., Any]:
    def factory(**overrides: Any) -> Any:
        data = {
            "title": "Test Document",
            "summary": "This is a test document.",
            "abstract": "This is a detailed test abstract.",
            "language": "English",
            "date": "1981-11-19",
            "archive_code": "TEST-1",
        }
        data.update(overrides)
        return create_mock_ollama_response(MetadataSchema(**data).model_dump_json())

    return factory


@pytest.fixture
def tagging_result() -> AggregatedTaggingResult:
    return AggregatedTaggingResult(
        conceptual_tags=["NATO"],
        entity_tags=["Org/NATO"],
        topic_tags=[
            TopicResult(
                topic="Defence Policy/Nuclear Planning",
                reason='The text mentions "nuclear planning group".',
            )
        ],
    )
