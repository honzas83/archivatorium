from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ocrpolish.models.metadata import TopicResult, WindowTaggingResult
from ocrpolish.services.tagging_service import TaggingService


@pytest.fixture
def mock_ollama():
    return MagicMock()


@pytest.fixture
def mock_windowing():
    return MagicMock()


def test_extract_tags_single_pass(mock_ollama, mock_windowing):
    # Set context limit high to force single pass
    service = TaggingService(
        mock_ollama, mock_windowing, Path("dummy.yaml"), Path("dummy.yaml"), context_limit=1000
    )
    text = "Short text"

    # Mock single pass result
    mock_result = WindowTaggingResult(
        conceptual_tags=["#Tag1"],
        entity_tags=["State/UK"],
        topic_tags=[TopicResult(topic="Category/Topic1", reason="Test reason")],
    )
    mock_ollama.extract_structured.return_value = mock_result

    # Implementation should use estimate_tokens(text)
    # For now, we stub it or rely on the logic we're about to write
    result = service.extract_tags(text)

    # Conceptual tags are normalized (hyphenated, no #)
    assert "Tag1" in result.conceptual_tags
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
            conceptual_tags=["#T1"],
            entity_tags=["E1"],
            topic_tags=[TopicResult(topic="Top1", reason="R1")],
        ),
        WindowTaggingResult(
            conceptual_tags=["#T2"],
            entity_tags=["E2"],
            topic_tags=[TopicResult(topic="Top2", reason="R2")],
        ),
    ]

    result = service.extract_tags(text)

    # Tags are normalized (hyphenated, no #)
    assert "T1" in result.conceptual_tags
    assert "T2" in result.conceptual_tags
    assert "E1" in result.entity_tags
    assert "E2" in result.entity_tags

    topics = {t.topic: t.reason for t in result.topic_tags}
    assert "Top1" in topics
    assert topics["Top1"] == "R1"
    assert "Top2" in topics
    assert topics["Top2"] == "R2"

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
    topics:
      - topic: Top
        description: Desc
""".lstrip()
    )
    tags_file = tmp_path / "tags.yaml"
    tags_file.write_text("useful_tags:\n  - NATO\n")

    dump_calls = 0

    def fake_dump(data, sort_keys=False):
        nonlocal dump_calls
        dump_calls += 1
        return "STATIC TAXONOMY"

    monkeypatch.setattr("ocrpolish.services.tagging_service.yaml.dump", fake_dump)

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
    hierarchy_file.write_text("categories: []")
    tags_file = tmp_path / "tags.yaml"
    tags_file.write_text("useful_tags:\n  - NATO\n")

    dump_calls = 0

    def fake_dump(data, sort_keys=False):
        nonlocal dump_calls
        dump_calls += 1
        return "STATIC TAXONOMY"

    monkeypatch.setattr("ocrpolish.services.tagging_service.yaml.dump", fake_dump)
    service = TaggingService(
        mock_ollama, mock_windowing, hierarchy_file, tags_file, context_limit=1
    )
    mock_windowing.get_windows.return_value = ["chunk1", "chunk2", "chunk3"]
    mock_ollama.extract_structured.return_value = WindowTaggingResult()

    service.extract_tags("long document")

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


def test_tagging_prompt_includes_flattened_taxonomy_details(
    mock_ollama, mock_windowing, tmp_path
):
    hierarchy_file = tmp_path / "hierarchy.yaml"
    hierarchy_file.write_text(
        """
categories:
  - category: "Cat1"
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


def test_extract_tags_returns_empty_result_on_llm_failure(mock_ollama, mock_windowing):
    service = TaggingService(
        mock_ollama, mock_windowing, Path("dummy.yaml"), Path("dummy.yaml"), context_limit=1000
    )
    mock_ollama.extract_structured.side_effect = Exception("Ollama error")

    result = service.extract_tags("Some text chunk")

    assert result.conceptual_tags == []
    assert result.entity_tags == []
    assert result.topic_tags == []
    mock_ollama.extract_structured.assert_called_once()
