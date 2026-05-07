from unittest.mock import MagicMock

import pytest

from ocrpolish.models.metadata import WindowTaggingResult
from ocrpolish.services.tagging_service import TaggingService


@pytest.fixture
def mock_ollama():
    return MagicMock()

@pytest.fixture
def mock_windowing():
    return MagicMock()

def test_tag_reuse_prompt_inclusion(mock_ollama, mock_windowing, tmp_path):
    themes_file = tmp_path / "themes.yaml"
    themes_file.write_text("themes: []")

    tags_file = tmp_path / "tags.yaml"
    tags_file.write_text("useful_tags:\n  - '#NATO'\n  - '#ColdWar'")

    service = TaggingService(
        mock_ollama, 
        mock_windowing, 
        themes_file, 
        tags_file, 
        context_limit=1000
    )

    mock_ollama.extract_structured.return_value = WindowTaggingResult(
        conceptual_tags=["#NATO"], entity_tags=[], topic_tags=[]
    )

    service.extract_tags("Text mentioning nato and cold war.")
    
    # Verify the prompt contains the vocabulary
    call_args = mock_ollama.extract_structured.call_args
    prompt = call_args[0][0]
    
    assert "EXISTING VOCABULARY" in prompt
    assert "NATO" in prompt
    assert "ColdWar" in prompt
