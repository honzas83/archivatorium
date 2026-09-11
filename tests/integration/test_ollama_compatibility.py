from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from archivatorium.ocr_engine import OCREngine


@pytest.mark.parametrize(
    ("mode", "expected_think", "expected_options"),
    [
        ("standard", None, {"num_ctx": 24576, "num_predict": 16384}),
        ("qwen38", "low", {"num_ctx": 24576, "num_predict": 16384}),
        (
            "glm",
            False,
            {
                "num_ctx": 24576,
                "temperature": 0.0,
                "top_p": 0.00001,
                "top_k": 1,
                "repeat_penalty": 1.1,
                "repeat_last_n": 512,
                "num_predict": 8192,
            },
        ),
        ("firered", None, {"num_ctx": 24576, "num_predict": 16384}),
    ],
)
def test_native_ocr_request_baseline(
    mode: str, expected_think: bool | str | None, expected_options: dict[str, int | float]
) -> None:
    with patch("archivatorium.ocr_engine.Client"):
        engine = OCREngine(mode=mode, model_think="low")
    messages = engine._build_messages(Path("page.png"), "PREVIOUS")

    request = engine._build_chat_request(messages, 24576)

    assert request["model"] == "qwen3.5:9b"
    assert request["messages"] == messages
    assert request["options"] == expected_options
    assert request["stream"] is False
    if expected_think is None:
        assert "think" not in request
    else:
        assert request["think"] == expected_think


def test_deterministic_ocr_output_bytes_and_page_order(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "document.md"
    page_images = [tmp_path / "one.png", tmp_path / "two.png"]
    for image in page_images:
        image.write_bytes(b"synthetic")

    with patch("archivatorium.ocr_engine.Client"):
        engine = OCREngine(mode="qwen38")
    engine.count_pdf_pages = MagicMock(return_value=2)  # type: ignore[method-assign]
    engine.render_pdf_page_to_png = MagicMock(  # type: ignore[method-assign]
        side_effect=page_images
    )
    engine.ocr_single_page = MagicMock(  # type: ignore[method-assign]
        side_effect=["PAGE ONE\n", "PAGE TWO"]
    )

    result = engine.run_ocr(Path("source.pdf"), output)

    expected = "---\n\n# Page 1\n\nPAGE ONE\n\n---\n\n# Page 2\n\nPAGE TWO"
    assert result == expected
    assert output.read_bytes() == expected.encode("utf-8")
    assert engine.ocr_single_page.call_args_list[1].kwargs["last_text"] == "PAGE ONE\n"


def test_resume_skips_completed_page_without_render_or_inference(tmp_path: Path) -> None:
    output = tmp_path / "document.md"
    output.write_text("---\n\n# Page 1\n\nEXISTING", encoding="utf-8")
    page_two = tmp_path / "two.png"
    page_two.write_bytes(b"synthetic")

    with patch("archivatorium.ocr_engine.Client"):
        engine = OCREngine(mode="standard")
    engine.count_pdf_pages = MagicMock(return_value=2)  # type: ignore[method-assign]
    engine.render_pdf_page_to_png = MagicMock(  # type: ignore[method-assign]
        return_value=page_two
    )
    engine.ocr_single_page = MagicMock(return_value="NEW")  # type: ignore[method-assign]

    result = engine.run_ocr(Path("source.pdf"), output)

    engine.render_pdf_page_to_png.assert_called_once_with(Path("source.pdf"), 2)
    engine.ocr_single_page.assert_called_once()
    assert engine.ocr_single_page.call_args.kwargs["last_text"] == "EXISTING"
    assert result.endswith("# Page 2\n\nNEW")
