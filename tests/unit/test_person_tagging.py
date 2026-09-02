from pathlib import Path
from unittest.mock import MagicMock

import pytest

from archivatorium.models.metadata import WindowTaggingResult
from archivatorium.services.tagging_service import TaggingService


@pytest.fixture
def service(tmp_path: Path) -> tuple[TaggingService, MagicMock, MagicMock]:
    hierarchy = tmp_path / "hierarchy.yaml"
    hierarchy.write_text(
        """
categories:
  - category: People
    description: People-related subjects
    topics:
      - topic: Appointments
        description: Appointment of officials
        positive_samples: A substantive appointment decision
        negative_samples: A passing mention of an official
""",
        encoding="utf-8",
    )
    tags = tmp_path / "tags.yaml"
    tags.write_text("useful_tags: []\n", encoding="utf-8")
    client = MagicMock()
    windowing = MagicMock()
    tagging = TaggingService(client, windowing, hierarchy, tags, context_limit=1000)
    return tagging, client, windowing


def test_person_prompt_defines_surname_first_contract(
    service: tuple[TaggingService, MagicMock, MagicMock],
) -> None:
    tagging, _, _ = service

    prompt = tagging._generate_tagging_prompt("K-W Andrae and Joseph M.A.H. Luns attended.")

    assert "Person/<surname>[/<given-name-or-initials>]" in prompt
    assert "Person/Andrae/K-W" in prompt
    assert "Person/Luns/Joseph-M-A-H" in prompt
    assert "Person/Andrae" in prompt
    assert "minister" in prompt.lower()
    assert "secretary" in prompt.lower()


def test_single_pass_normalizes_and_drops_malformed_people(
    service: tuple[TaggingService, MagicMock, MagicMock], caplog: pytest.LogCaptureFixture
) -> None:
    tagging, client, _ = service
    client.extract_structured.return_value = WindowTaggingResult(
        conceptual_tags=["Diplomacy"],
        entity_tags=[
            "Person/Andrae/K. W.",
            "Person/Luns/Joseph M.A.H.",
            "Person/Andrae",
            "Person/Andrae/K-W/Minister",
        ],
    )

    result = tagging.extract_tags("Names.")

    assert result.entity_tags == [
        "Person/Andrae",
        "Person/Andrae/K-W",
        "Person/Luns/Joseph-M-A-H",
    ]
    assert "Dropping malformed Person entity" in caplog.text


def test_windowed_aggregation_uses_same_person_normalization(
    service: tuple[TaggingService, MagicMock, MagicMock],
) -> None:
    tagging, client, windowing = service
    tagging.context_limit = 1
    windowing.get_windows.return_value = ["first", "second"]
    client.extract_structured.side_effect = [
        WindowTaggingResult(conceptual_tags=["Diplomacy"], entity_tags=["Person/Andrae/K-W"]),
        WindowTaggingResult(
            conceptual_tags=["Diplomacy"],
            entity_tags=["Person/Andrae/K. W.", "Person/Luns/Minister"],
        ),
    ]

    result = tagging.extract_tags("brief names")

    assert result.entity_tags == ["Person/Andrae/K-W", "Person/Luns"]
