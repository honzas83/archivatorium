from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from archivatorium.models.metadata import (
    AggregatedTaggingResult,
    SubstantiveWindowTaggingResult,
    TopicResult,
    WindowTaggingResult,
)
from archivatorium.processor_metadata import TaggingReuseHints
from archivatorium.services.flattening_service import TaxonomyValidationError
from archivatorium.services.tagging_service import TaggingQualityError, TaggingService


@pytest.fixture
def mock_ollama():
    return MagicMock()


@pytest.fixture
def mock_windowing():
    return MagicMock()


@pytest.fixture(autouse=True)
def local_dummy_taxonomy(tmp_path, monkeypatch):
    """Materialize the legacy dummy path used by pre-existing unit tests."""
    monkeypatch.chdir(tmp_path)
    Path("dummy.yaml").write_text(
        """
categories:
  - category: Category
    description: Test category
    topics:
      - topic: Topic1
        description: Test topic
        positive_samples: substantive topic treatment
        negative_samples: incidental topic mention
      - topic: Topic2
        description: Second test topic
        positive_samples: another substantive treatment
        negative_samples: another incidental mention
useful_tags: []
""".lstrip(),
        encoding="utf-8",
    )


def test_missing_hierarchy_fails_during_service_initialization(
    mock_ollama, mock_windowing, tmp_path
):
    with pytest.raises(TaxonomyValidationError, match="Failed to load taxonomy"):
        TaggingService(mock_ollama, mock_windowing, tmp_path / "missing.yaml")


def test_service_precomputes_normalized_approved_topic_ids(
    mock_ollama, mock_windowing, hierarchy_file, useful_tags_file
):
    service = TaggingService(
        mock_ollama,
        mock_windowing,
        hierarchy_file,
        useful_tags_file,
    )

    assert service.approved_topic_ids == {"Defence-Policy/Nuclear-Planning"}


def test_v2_prompt_applies_substantive_subject_and_omission_policy(
    mock_ollama, mock_windowing, v2_hierarchy_file
):
    service = TaggingService(mock_ollama, mock_windowing, v2_hierarchy_file)

    prompt = service._generate_tagging_prompt("A meeting mentions nuclear deterrence once.")

    assert "Assign only important subjects treated substantively" in prompt
    assert "Prefer omission; an empty thematic-topic list is valid" in prompt
    assert "mention, entity, title, citation, or meeting is insufficient alone" in prompt
    assert "Do not include a topic for a keyword or passing reference alone" in prompt


def test_legacy_prompt_receives_universal_substantive_policy(
    mock_ollama, mock_windowing, hierarchy_file
):
    service = TaggingService(mock_ollama, mock_windowing, hierarchy_file)

    prompt = service._generate_tagging_prompt("Routine agenda mentioning nuclear planning.")

    assert "important subject of the document" in prompt
    assert "Prefer omission" in prompt
    assert "empty thematic-topic list" in prompt


def test_extract_tags_drops_unknown_topic_without_retry(
    mock_ollama, mock_windowing, hierarchy_file
):
    service = TaggingService(mock_ollama, mock_windowing, hierarchy_file, context_limit=1000)
    mock_ollama.extract_structured.return_value = WindowTaggingResult(
        conceptual_tags=["planning"],
        topic_tags=[TopicResult(topic="Invented/Topic", reason="Incidental mention")],
    )

    result = service.extract_tags("Substantive discussion of planning policy.")

    assert result.topic_tags == []
    mock_ollama.extract_structured.assert_called_once()


def test_sliding_window_keeps_earliest_supported_topic_reason(
    mock_ollama, mock_windowing, hierarchy_file
):
    service = TaggingService(mock_ollama, mock_windowing, hierarchy_file, context_limit=1)
    mock_windowing.get_windows.return_value = ["first", "second"]
    mock_ollama.extract_structured.side_effect = [
        WindowTaggingResult(
            conceptual_tags=["planning"],
            topic_tags=[
                TopicResult(topic="Defence Policy/Nuclear Planning", reason="Earliest reason")
            ],
        ),
        WindowTaggingResult(
            conceptual_tags=["planning"],
            topic_tags=[
                TopicResult(topic="Defence-Policy/Nuclear-Planning", reason="Later reason")
            ],
        ),
    ]

    result = service.extract_tags("Substantive document long enough for windows.")

    assert [(topic.topic, topic.reason) for topic in result.topic_tags] == [
        ("Defence-Policy/Nuclear-Planning", "Earliest reason")
    ]


def test_extract_tags_single_pass(mock_ollama, mock_windowing):
    # Set context limit high to force single pass
    service = TaggingService(
        mock_ollama, mock_windowing, Path("dummy.yaml"), Path("dummy.yaml"), context_limit=1000
    )
    text = (
        "NATO nuclear planning consultation procedures require exercises, "
        "deterrence strategy, and operational doctrine."
    )

    # Mock single pass result
    mock_result = WindowTaggingResult(
        conceptual_tags=[
            "#Nuclear-Planning",
            "#Consultation-Procedures",
            "#Exercises",
        ],
        entity_tags=["State/UK"],
        topic_tags=[TopicResult(topic="Category/Topic1", reason="Test reason")],
    )
    mock_ollama.extract_structured.return_value = mock_result

    # Implementation should use estimate_tokens(text)
    # For now, we stub it or rely on the logic we're about to write
    result = service.extract_tags(text)

    # Conceptual tags are normalized (hyphenated, no #)
    assert "Nuclear-Planning" in result.conceptual_tags
    assert "State/UK" in result.entity_tags
    assert result.topic_tags[0].topic == "Category/Topic1"
    assert result.topic_tags[0].reason == "Test reason"
    mock_ollama.extract_structured.assert_called_once()
    mock_windowing.get_windows.assert_not_called()


def test_extract_tags_sliding_window(mock_ollama, mock_windowing):
    # Set context limit low to force sliding window
    service = TaggingService(
        mock_ollama, mock_windowing, Path("dummy.yaml"), Path("dummy.yaml"), context_limit=5
    )
    text = "Very long text that exceeds limit"

    # Mock windowing
    mock_windowing.get_windows.return_value = ["chunk1", "chunk2"]

    # Mock results for each chunk
    mock_ollama.extract_structured.side_effect = [
        WindowTaggingResult(
            conceptual_tags=["#T1", "#T2", "#T3"],
            entity_tags=["E1"],
            topic_tags=[TopicResult(topic="Category/Topic1", reason="R1")],
        ),
        WindowTaggingResult(
            conceptual_tags=["#T2", "#T6", "#T7"],
            entity_tags=["E2"],
            topic_tags=[TopicResult(topic="Category/Topic2", reason="R2")],
        ),
    ]

    result = service.extract_tags(text)

    # Tags are normalized (hyphenated, no #)
    assert "T1" in result.conceptual_tags
    assert "T2" in result.conceptual_tags
    assert "E1" in result.entity_tags
    assert "E2" in result.entity_tags

    topics = {t.topic: t.reason for t in result.topic_tags}
    assert "Category/Topic1" in topics
    assert topics["Category/Topic1"] == "R1"
    assert "Category/Topic2" in topics
    assert topics["Category/Topic2"] == "R2"

    assert mock_ollama.extract_structured.call_count == 2
    mock_windowing.get_windows.assert_called_once_with(text)


def test_static_prompt_sections_precomputed_once(
    mock_ollama, mock_windowing, tmp_path, monkeypatch
):
    hierarchy_file = tmp_path / "hierarchy.yaml"
    hierarchy_file.write_text(
        """
categories:
  - category: Cat
    description: Category description
    topics:
      - topic: Top
        description: Desc
        positive_samples: Positive
        negative_samples: Negative
""".lstrip()
    )
    tags_file = tmp_path / "tags.yaml"
    tags_file.write_text("useful_tags:\n  - NATO\n")

    dump_calls = 0

    def fake_dump(data, sort_keys=False):
        nonlocal dump_calls
        dump_calls += 1
        return "STATIC TAXONOMY"

    monkeypatch.setattr("archivatorium.services.tagging_service.yaml.dump", fake_dump)

    service = TaggingService(mock_ollama, mock_windowing, hierarchy_file, tags_file)

    first_prompt = service._generate_tagging_prompt("chunk one")
    second_prompt = service._generate_tagging_prompt("chunk two")

    assert dump_calls == 1
    assert "STATIC TAXONOMY" in first_prompt
    assert "STATIC TAXONOMY" in second_prompt
    assert "chunk one" in first_prompt
    assert "chunk two" in second_prompt


def test_sliding_window_reuses_static_prompt_text(
    mock_ollama, mock_windowing, tmp_path, monkeypatch
):
    hierarchy_file = tmp_path / "hierarchy.yaml"
    hierarchy_file.write_text(
        """
categories:
  - category: Cat
    description: Category description
    topics:
      - topic: Top
        description: Desc
        positive_samples: Positive
        negative_samples: Negative
""".lstrip()
    )
    tags_file = tmp_path / "tags.yaml"
    tags_file.write_text("useful_tags:\n  - NATO\n")

    dump_calls = 0

    def fake_dump(data, sort_keys=False):
        nonlocal dump_calls
        dump_calls += 1
        return "STATIC TAXONOMY"

    monkeypatch.setattr("archivatorium.services.tagging_service.yaml.dump", fake_dump)
    service = TaggingService(
        mock_ollama, mock_windowing, hierarchy_file, tags_file, context_limit=1
    )
    mock_windowing.get_windows.return_value = ["chunk1", "chunk2", "chunk3"]
    mock_ollama.extract_structured.return_value = WindowTaggingResult(
        conceptual_tags=["#Administrative-Stub"]
    )

    service.extract_tags("this document is incorporated into the initial document")

    assert dump_calls == 1
    prompts = [call.args[0] for call in mock_ollama.extract_structured.call_args_list]
    assert len(prompts) == 3
    assert all(prompt.count("STATIC TAXONOMY") == 1 for prompt in prompts)
    assert all("EXISTING VOCABULARY" in prompt for prompt in prompts)


def test_prompt_uses_flat_category_topic_format(mock_ollama, mock_windowing):
    service = TaggingService(
        mock_ollama, mock_windowing, Path("dummy.yaml"), Path("dummy.yaml"), context_limit=1000
    )

    prompt = service._generate_tagging_prompt("Sample")

    assert "Use format: Category/Topic" in prompt
    assert "Category/<category>/<topic>" not in prompt


def test_tagging_prompt_includes_flattened_taxonomy_details(mock_ollama, mock_windowing, tmp_path):
    hierarchy_file = tmp_path / "hierarchy.yaml"
    hierarchy_file.write_text(
        """
categories:
  - category: "Cat1"
    description: "Category Desc1"
    topics:
      - topic: "Top1"
        description: "Desc1"
        positive_samples: "Pos1"
        negative_samples: "Neg1"
""".lstrip()
    )
    tags_file = tmp_path / "tags.yaml"
    tags_file.write_text("useful_tags:\n  - NATO\n")

    service = TaggingService(mock_ollama, mock_windowing, hierarchy_file, tags_file)
    prompt = service._generate_tagging_prompt("Sample text")

    assert "Sample text" in prompt
    assert "APPROVED TAXONOMY (YAML):" in prompt
    assert "Cat1/Top1" in prompt
    assert "Desc1" in prompt
    assert "Pos1" in prompt
    assert "Neg1" in prompt


def test_prompt_serializes_policy_and_topics_as_one_payload(
    mock_ollama, mock_windowing, v2_hierarchy_file, monkeypatch
):
    dumped = []

    def capture_dump(data, sort_keys=False):
        dumped.append(data)
        return "COMPLETE TAXONOMY PAYLOAD"

    monkeypatch.setattr("archivatorium.services.tagging_service.yaml.dump", capture_dump)

    service = TaggingService(mock_ollama, mock_windowing, v2_hierarchy_file)
    prompt = service._generate_tagging_prompt("Substantive text")

    assert len(dumped) == 1
    assert set(dumped[0]) == {"classification_policy", "topics"}
    assert dumped[0]["classification_policy"] == service.classification_policy
    assert dumped[0]["topics"] == service.flattened_taxonomy
    assert prompt.count("COMPLETE TAXONOMY PAYLOAD") == 1


def test_extract_tags_raises_quality_error_on_substantive_llm_failure(mock_ollama, mock_windowing):
    service = TaggingService(
        mock_ollama, mock_windowing, Path("dummy.yaml"), Path("dummy.yaml"), context_limit=1000
    )
    mock_ollama.extract_structured.side_effect = Exception("Ollama error")

    with pytest.raises(TaggingQualityError):
        service.extract_tags("NATO nuclear planning consultation procedures")

    mock_ollama.extract_structured.assert_called_once()


def test_substantive_schema_requires_one_conceptual_tag() -> None:
    assert SubstantiveWindowTaggingResult(topic_tags=[], conceptual_tags=["a"]).conceptual_tags == [
        "a"
    ]
    with pytest.raises(ValidationError):
        SubstantiveWindowTaggingResult(topic_tags=[], conceptual_tags=[])


def test_prompt_requires_conceptual_tags_and_removes_permissive_wording(
    mock_ollama: MagicMock, mock_windowing: MagicMock
) -> None:
    service = TaggingService(
        mock_ollama, mock_windowing, Path("dummy.yaml"), Path("dummy.yaml"), context_limit=1000
    )
    prompt = service._generate_tagging_prompt("NATO nuclear planning")

    assert "Return at least 1 conceptual tag(s) for substantive documents" in prompt
    assert "include every clearly justified useful conceptual tag" in prompt
    assert "Up to 15" not in prompt


def test_topic_tagging_guidance_has_no_hard_maximum(
    mock_ollama: MagicMock, mock_windowing: MagicMock
) -> None:
    service = TaggingService(
        mock_ollama, mock_windowing, Path("dummy.yaml"), Path("dummy.yaml"), context_limit=1000
    )
    prompt = service._generate_tagging_prompt("NATO nuclear planning")
    window_topic_description = WindowTaggingResult.model_fields["topic_tags"].description or ""
    aggregated_topic_description = (
        AggregatedTaggingResult.model_fields["topic_tags"].description or ""
    )

    assert "Max 10" not in prompt
    assert "maximum" not in window_topic_description.lower()
    assert "maximum" not in aggregated_topic_description.lower()
    assert "every substantively supported taxonomy topic" in prompt


def test_extract_tags_retains_more_than_ten_topic_assignments(
    mock_ollama: MagicMock, mock_windowing: MagicMock
) -> None:
    service = TaggingService(
        mock_ollama, mock_windowing, Path("dummy.yaml"), Path("dummy.yaml"), context_limit=1000
    )
    service.approved_topic_ids = {f"Category/Topic-{idx}" for idx in range(12)}
    mock_ollama.extract_structured.return_value = WindowTaggingResult(
        conceptual_tags=["tag-a", "tag-b", "tag-c"],
        topic_tags=[
            TopicResult(topic=f"Category/Topic-{idx}", reason=f"Reason {idx}") for idx in range(12)
        ],
    )

    result = service.extract_tags("NATO nuclear planning consultation procedures")

    assert len(result.topic_tags) == 12
    assert {topic.topic for topic in result.topic_tags} == {
        f"Category/Topic-{idx}" for idx in range(12)
    }


def test_substantive_validation_rejects_empty_conceptual_tags(
    mock_ollama: MagicMock, mock_windowing: MagicMock
) -> None:
    service = TaggingService(
        mock_ollama, mock_windowing, Path("dummy.yaml"), Path("dummy.yaml"), context_limit=1000
    )
    mock_ollama.extract_structured.return_value = WindowTaggingResult(conceptual_tags=[])

    with pytest.raises(TaggingQualityError):
        service.extract_tags("NATO nuclear planning consultation procedures")


def test_non_substantive_stub_allows_empty_conceptual_tags(
    mock_ollama: MagicMock, mock_windowing: MagicMock
) -> None:
    service = TaggingService(
        mock_ollama, mock_windowing, Path("dummy.yaml"), Path("dummy.yaml"), context_limit=1000
    )
    mock_ollama.extract_structured.return_value = WindowTaggingResult()

    result = service.extract_tags("This document is incorporated into the initial document")

    assert result.conceptual_tags == []


@pytest.mark.parametrize(
    "text",
    [
        "NATO",
        "nuclear policy",
        "consultation",
        "exercise",
        "command",
        "weapons",
        "references",
    ],
)
def test_short_substantive_text_is_substantive(
    mock_ollama: MagicMock, mock_windowing: MagicMock, text: str
) -> None:
    service = TaggingService(
        mock_ollama, mock_windowing, Path("dummy.yaml"), Path("dummy.yaml"), context_limit=1000
    )
    assert service._is_substantive(text)


def test_reuse_hints_are_category_specific_in_prompt(
    mock_ollama: MagicMock, mock_windowing: MagicMock
) -> None:
    service = TaggingService(
        mock_ollama, mock_windowing, Path("dummy.yaml"), Path("dummy.yaml"), context_limit=1000
    )
    hints = TaggingReuseHints(
        preferred_conceptual_tags=["nuclear-planning"],
        preferred_entities={"Org": ["nato"], "State": ["belgium"]},
        preferred_topics=["defence-policy/nuclear-planning"],
    )

    prompt = service._generate_tagging_prompt("NATO nuclear planning", reuse_hints=hints)

    assert "RESUMED #Tags PREFERRED VOCABULARY" in prompt
    assert "nuclear-planning" in prompt
    assert "RESUMED #Entities PREFERRED VOCABULARY" in prompt
    assert "- Org: nato" in prompt
    assert "RESUMED #Topics HINTS (subordinate to taxonomy)" in prompt
