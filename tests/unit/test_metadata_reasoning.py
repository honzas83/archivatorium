import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from archivatorium.models.metadata import (
    LastDateSchema,
    MetadataSchema,
    WindowTaggingResult,
)
from archivatorium.processor_metadata import CHUNK_SIZE, MetadataProcessor
from archivatorium.services.ollama_client import OllamaClient
from archivatorium.services.tagging_service import TaggingService
from archivatorium.utils.model_think import ModelThink


def test_metadata_reasoning_defaults_to_medium(tmp_path: Path) -> None:
    processor = MetadataProcessor(MagicMock(), tmp_path)

    assert processor.model_think == "medium"


def test_primary_metadata_extraction_receives_reasoning(tmp_path: Path) -> None:
    client = MagicMock()
    client.extract_structured.return_value = MetadataSchema(date="1978-01-02")
    processor = MetadataProcessor(client, tmp_path, model_think="high")

    processor._extract_document_metadata(Path("document.md"), "short document")

    assert client.extract_structured.call_args.kwargs["think"] == "high"


def test_conditional_date_extraction_receives_same_reasoning(tmp_path: Path) -> None:
    client = MagicMock()
    client.extract_structured.side_effect = [MetadataSchema(), LastDateSchema(date="1978-01-02")]
    processor = MetadataProcessor(client, tmp_path, model_think=False)

    result = processor._extract_document_metadata(Path("document.md"), "x" * (CHUNK_SIZE + 3000))

    assert result.raw_dict["date"] == "1978-01-02"
    assert [call.kwargs["think"] for call in client.extract_structured.call_args_list] == [
        False,
        False,
    ]


def test_structured_extraction_retries_keep_reasoning_value() -> None:
    client = OllamaClient.__new__(OllamaClient)
    client.model = "test-model"
    client.client = MagicMock()
    client.client.chat.side_effect = [
        {"message": {"content": "[]"}},
        {"message": {"content": json.dumps({"date": "1978-01-02"})}},
    ]

    result = client.extract_structured("date", LastDateSchema, retries=1, think="low")

    assert result.date == "1978-01-02"
    assert [call.kwargs["think"] for call in client.client.chat.call_args_list] == ["low", "low"]


@pytest.mark.parametrize("model_think", [False, "low", "medium", "high"])
def test_tagging_inference_receives_reasoning_value(
    tmp_path: Path, model_think: ModelThink
) -> None:
    hierarchy = tmp_path / "hierarchy.yaml"
    hierarchy.write_text(
        """
classification_policy:
  substantive_subject_rule: Important subject only.
  omission_rule: Omit weak matches.
  insufficient_evidence_rule: Passing mentions are insufficient.
categories:
  - category: Diplomacy
    description: Diplomatic subjects
    topics:
      - topic: Negotiation
        description: Substantive negotiations
        positive_samples: A negotiated agreement
        negative_samples: A passing mention
""",
        encoding="utf-8",
    )
    client = MagicMock()
    client.extract_structured.return_value = WindowTaggingResult()
    service = TaggingService(client, MagicMock(), hierarchy, model_think=model_think)

    result = service._extract_chunk("stub", require_conceptual_tags=False)

    assert result == WindowTaggingResult()
    assert client.extract_structured.call_args.kwargs["think"] == model_think


def test_tagging_reasoning_defaults_to_medium(tmp_path: Path) -> None:
    hierarchy = tmp_path / "hierarchy.yaml"
    hierarchy.write_text(
        """
categories:
  - category: Diplomacy
    description: Diplomatic subjects
    topics:
      - topic: Negotiation
        description: Substantive negotiations
        positive_samples: A negotiated agreement
        negative_samples: A passing mention
""".lstrip(),
        encoding="utf-8",
    )
    client = MagicMock()
    client.extract_structured.return_value = WindowTaggingResult()

    service = TaggingService(client, MagicMock(), hierarchy)
    service._extract_chunk("stub", require_conceptual_tags=False)

    assert client.extract_structured.call_args.kwargs["think"] == "medium"
