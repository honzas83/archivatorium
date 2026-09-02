from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from archivatorium.ocr_engine import OCREngine


def _response(content: str) -> MagicMock:
    response = MagicMock()
    response.message = {"content": content, "thinking": "private reasoning"}
    return response


@pytest.mark.parametrize("model_think", [False, "low", "medium", "high"])
def test_qwen38_reasoning_override_is_sent(model_think: bool | str) -> None:
    with patch("archivatorium.ocr_engine.Client") as client_class:
        client_class.return_value.chat.return_value = _response("Visible text")
        engine = OCREngine(mode="qwen38", model_think=model_think)
        assert engine.ocr_single_page(Path("page.png")) == "Visible text"

    assert client_class.return_value.chat.call_args.kwargs["think"] == model_think


@pytest.mark.parametrize(
    ("mode", "expected"),
    [("standard", None), ("glm", False), ("firered", None)],
)
def test_model_think_does_not_change_unrelated_ocr_profiles(
    mode: str, expected: bool | None
) -> None:
    with patch("archivatorium.ocr_engine.Client") as client_class:
        client_class.return_value.chat.return_value = _response("Visible text")
        engine = OCREngine(mode=mode, model_think="high")
        engine.ocr_single_page(Path("page.png"))

    request = client_class.return_value.chat.call_args.kwargs
    if expected is None:
        assert "think" not in request
    else:
        assert request["think"] is expected


def test_qwen38_retry_preserves_override_and_strips_reasoning() -> None:
    with patch("archivatorium.ocr_engine.Client") as client_class:
        client_class.return_value.chat.side_effect = [
            RuntimeError("temporary"),
            _response("hidden</think>Visible text"),
        ]
        engine = OCREngine(mode="qwen38", model_think="low")
        with patch("archivatorium.ocr_engine.time.sleep"):
            result = engine.ocr_single_page(Path("page.png"), retry=2)

    assert result == "Visible text"
    calls = client_class.return_value.chat.call_args_list
    assert calls[0].kwargs == calls[1].kwargs
    assert calls[0].kwargs["think"] == "low"
    assert "hidden" not in result
