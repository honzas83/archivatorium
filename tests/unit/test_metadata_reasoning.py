import json
from pathlib import Path
from unittest.mock import MagicMock

from archivatorium.models.metadata import (
    LastDateSchema,
    MetadataSchema,
    WindowTaggingResult,
)
from archivatorium.processor_metadata import CHUNK_SIZE, MetadataProcessor
from archivatorium.services.ollama_client import OllamaClient
from archivatorium.services.tagging_service import TaggingService


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


def test_metadata_reasoning_does_not_change_tagging_reasoning(tmp_path: Path) -> None:
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
    service = TaggingService(client, MagicMock(), hierarchy)

    result = service._extract_chunk("stub", require_conceptual_tags=False)

    assert result == WindowTaggingResult()
    assert client.extract_structured.call_args.kwargs["think"] is False
