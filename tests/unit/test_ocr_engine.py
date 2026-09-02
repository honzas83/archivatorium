from collections.abc import Callable
from pathlib import Path
from typing import Literal, get_type_hints
from unittest.mock import MagicMock, patch, mock_open

import pytest
from archivatorium.ocr_engine import (
    FIRERED_OCR_PROFILE,
    FIRERED_USER_PROMPT,
    GLM_OCR_PROFILE,
    OCRModeProfile,
    OCREngine,
    QWEN38_OCR_PROFILE,
    QWEN38_SYSTEM_PROMPT,
    QWEN38_USER_PROMPT,
    STANDARD_OCR_PROFILE,
    SYSTEM_PROMPT,
    USER_PROMPT,
    normalize_ocr_response,
    resolve_ocr_mode,
)


GLM_DEFAULT_OPTIONS = {
    "num_ctx": 8192,
    "temperature": 0.0,
    "top_p": 0.00001,
    "top_k": 1,
    "repeat_penalty": 1.1,
    "repeat_last_n": 512,
    "num_predict": 8192,
}

FIRERED_EXPECTED_PROMPT = (
    "You are an expert in converting PDF images to Markdown format.\n\n"
    "Please convert the provided document image into Markdown while preserving the original "
    "document structure.\n\n"
    "Requirements:\n"
    "- Preserve headings, paragraphs, lists, and reading order.\n"
    "- Convert tables to HTML table format.\n"
    "- Convert mathematical formulas to LaTeX.\n"
    "- Ignore figures and images.\n"
    "- Do not add, summarize, correct, or infer any content that is not present in the document.\n"
    "- Output only the converted Markdown."
)

QWEN38_EXPECTED_SYSTEM_PROMPT = (
    "You are a precise OCR transcription system. Transcribe only content visible in the current "
    "document image, in reading order. Return only the Markdown transcription; do not add "
    "commentary or generated HTML.\n\n"
    "Output contract:\n"
    "1. Preserve visible wording, capitalization, punctuation, typos, headings, paragraphs, "
    "lists, numbering, tables, footnotes, annotations, section breaks, and legible figure "
    "captions. Do not summarize, correct, rephrase, infer, or invent content.\n"
    "2. Keep visually supported headings as plain text on their own lines. Do not generate "
    "Markdown heading markers (#, ##, or other levels), bold (** or __), or italic (* or _) "
    "emphasis. Typewritten text has no Markdown styling; do not infer styling from capitalization, "
    "spacing, underlining, or position. Use explicit Markdown markers only for visible lists.\n"
    "3. Put each prose paragraph on one physical line by removing visual line wraps. Separate "
    "distinct prose paragraphs with exactly one blank line. Keep plain-text headings, list items, "
    "table rows, and fenced-block lines as separate Markdown "
    "blocks.\n"
    "4. Use a Markdown pipe table when the table structure is clear. Otherwise preserve it in a "
    "fenced plain-text block. Never generate HTML.\n"
    "5. Start every top-level block at column 1; do not reproduce page margins or layout "
    "indentation. Use indentation only where Markdown syntax requires nested list structure or "
    "inside a fenced literal block.\n"
    "6. IMPORTANT: In any text, collapse artificial typewriter-style spacing between letters "
    "while preserving word boundaries. Apply this to headings, prose, labels, and table cells. "
    "Example: N A T O   S E C R E T → NATO SECRET.\n"
    "7. Typewriters used for these documents do not have curly braces. Never infer or normalize "
    "characters into { or }. Output a curly brace only when it is unambiguously visible in the "
    "current image.\n"
    "8. Do not invent or modernize punctuation or symbols unavailable on the source typewriter. "
    "Output any unusual character only when it is unambiguously visible; otherwise write "
    "[unreadable].\n"
    "9. Preserve meaningful whitespace inside literal content and write [unreadable] for "
    "illegible text. Return an empty transcription only when the page is truly blank.\n"
    "10. Previous-page text, when supplied, is context only. Never copy it unless the same text "
    "is visible in the current image."
)

QWEN38_EXPECTED_USER_PROMPT = (
    "Transcribe this document image according to the output contract. "
    "Return only the Markdown transcription."
)


def test_qwen38_prompt_defines_plain_typewriter_structure_and_generic_despacing() -> None:
    assert QWEN38_SYSTEM_PROMPT.startswith("You are a precise OCR transcription system.")
    assert "Return only the Markdown transcription" in QWEN38_SYSTEM_PROMPT
    assert "do not add commentary or generated HTML" in QWEN38_SYSTEM_PROMPT
    assert "headings as plain text on their own lines" in QWEN38_SYSTEM_PROMPT
    assert "Do not generate Markdown heading markers" in QWEN38_SYSTEM_PROMPT
    assert "bold (** or __), or italic (* or _) emphasis" in QWEN38_SYSTEM_PROMPT
    assert "Typewritten text has no Markdown styling" in QWEN38_SYSTEM_PROMPT
    assert "# for the document title" not in QWEN38_SYSTEM_PROMPT
    assert "Markdown pipe table" in QWEN38_SYSTEM_PROMPT
    assert "fenced plain-text block" in QWEN38_SYSTEM_PROMPT
    assert "Start every top-level block at column 1" in QWEN38_SYSTEM_PROMPT
    assert "In any text, collapse artificial typewriter-style spacing" in (QWEN38_SYSTEM_PROMPT)
    assert "headings, prose, labels, and table cells" in QWEN38_SYSTEM_PROMPT
    assert "N A T O   S E C R E T → NATO SECRET" in QWEN38_SYSTEM_PROMPT
    assert "Never infer or normalize characters into { or }" in QWEN38_SYSTEM_PROMPT
    assert "only when it is unambiguously visible" in QWEN38_SYSTEM_PROMPT
    assert "Do not invent or modernize punctuation or symbols" in QWEN38_SYSTEM_PROMPT
    assert "unavailable on the source typewriter" in QWEN38_SYSTEM_PROMPT
    assert "otherwise write [unreadable]" in QWEN38_SYSTEM_PROMPT
    assert QWEN38_USER_PROMPT == (
        "Transcribe this document image according to the output contract. "
        "Return only the Markdown transcription."
    )


def test_qwen38_profile_is_distinct_without_changing_existing_profiles() -> None:
    profile = resolve_ocr_mode("qwen38")

    assert profile.name == "qwen38"
    assert profile.system_prompt == QWEN38_SYSTEM_PROMPT
    assert profile.user_prompt == QWEN38_USER_PROMPT
    assert profile.include_previous_page_context is True
    assert profile.default_options() == {"num_predict": 4096 * 4}
    assert resolve_ocr_mode(None) is STANDARD_OCR_PROFILE
    assert resolve_ocr_mode("standard") is STANDARD_OCR_PROFILE
    assert resolve_ocr_mode("glm") is GLM_OCR_PROFILE
    assert resolve_ocr_mode("firered") is FIRERED_OCR_PROFILE


def test_qwen38_prompt_matches_complete_single_line_paragraph_contract() -> None:
    assert QWEN38_SYSTEM_PROMPT == QWEN38_EXPECTED_SYSTEM_PROMPT
    assert QWEN38_USER_PROMPT == QWEN38_EXPECTED_USER_PROMPT
    assert "each prose paragraph on one physical line" in QWEN38_SYSTEM_PROMPT
    assert "distinct prose paragraphs with exactly one blank line" in QWEN38_SYSTEM_PROMPT
    assert (
        "plain-text headings, list items, table rows, and fenced-block lines as separate Markdown "
        "blocks" in QWEN38_SYSTEM_PROMPT
    )


def test_qwen38_profile_uses_precise_medium_reasoning_type_without_changing_other_modes() -> None:
    assert get_type_hints(OCRModeProfile)["think"] == (
        bool | Literal["low", "medium", "high"] | None
    )
    assert QWEN38_OCR_PROFILE.think == "medium"
    assert STANDARD_OCR_PROFILE.think is None
    assert GLM_OCR_PROFILE.think is False
    assert FIRERED_OCR_PROFILE.think is None


def test_qwen38_retry_reuses_identical_medium_reasoning_request(
    mock_ollama_client: MagicMock,
    ocr_response_factory: Callable[[str], MagicMock],
) -> None:
    engine = OCREngine(mode="qwen38", model="registry.example/qwen3.8:custom")
    mock_ollama_client.chat.side_effect = [
        RuntimeError("temporary"),
        ocr_response_factory("Recovered"),
    ]

    with patch("archivatorium.ocr_engine.time.sleep"):
        assert (
            engine.ocr_single_page(
                Path("page.png"),
                last_text="Clean context",
                retry=2,
            )
            == "Recovered"
        )

    first = mock_ollama_client.chat.call_args_list[0].kwargs
    second = mock_ollama_client.chat.call_args_list[1].kwargs
    assert first == second
    assert first["model"] == "registry.example/qwen3.8:custom"
    assert first["think"] == "medium"


def test_qwen38_discards_separate_reasoning_field(mock_ollama_client: MagicMock) -> None:
    engine = OCREngine(mode="qwen38")
    response = MagicMock()
    response.message = {
        "content": "Visible transcription",
        "thinking": "PRIVATE CHAIN OF THOUGHT",
    }
    mock_ollama_client.chat.return_value = response

    transcription = engine.ocr_single_page(Path("page.png"))

    assert transcription == "Visible transcription"
    assert "PRIVATE CHAIN OF THOUGHT" not in transcription


def test_qwen38_next_page_context_uses_content_after_final_think_marker(
    mock_pdf_reader: MagicMock,
    mock_convert_from_path: MagicMock,
    mock_ollama_client: MagicMock,
    ocr_response_factory: Callable[[str], MagicMock],
) -> None:
    engine = OCREngine(mode="qwen38")
    mock_ollama_client.chat.side_effect = [
        ocr_response_factory("first thought</think>second thought</think>PAGE ONE"),
        ocr_response_factory("PAGE TWO"),
    ]

    with (
        patch("builtins.open", mock_open(read_data=b"dummy")),
        patch("pathlib.Path.unlink"),
    ):
        engine.run_ocr(Path("dummy.pdf"))

    second_request = mock_ollama_client.chat.call_args_list[1].kwargs
    assert second_request["think"] == "medium"
    assert "PAGE ONE" in str(second_request["messages"])
    assert "first thought" not in str(second_request["messages"])
    assert "second thought" not in str(second_request["messages"])
    assert "</think>" not in str(second_request["messages"])


def assert_ocr_timing_log(
    mock_logger: MagicMock,
    *,
    attempted_pages: int,
    total_seconds: float,
    average_seconds_per_page: float | None,
) -> None:
    if average_seconds_per_page is None:
        mock_logger.assert_any_call(
            "OCR timing: attempted_pages=%d total_seconds=%.3f "
            "average_seconds_per_page=unavailable",
            attempted_pages,
            total_seconds,
        )
    else:
        mock_logger.assert_any_call(
            "OCR timing: attempted_pages=%d total_seconds=%.3f average_seconds_per_page=%.3f",
            attempted_pages,
            total_seconds,
            average_seconds_per_page,
        )


@pytest.fixture
def mock_ollama_client():
    with patch("archivatorium.ocr_engine.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_pdf_reader():
    with patch("archivatorium.ocr_engine.PdfReader") as mock_reader_class:
        mock_reader = MagicMock()
        mock_reader.pages = [MagicMock(), MagicMock()]  # 2 pages
        mock_reader_class.return_value = mock_reader
        yield mock_reader


@pytest.fixture
def mock_convert_from_path():
    with patch("archivatorium.ocr_engine.convert_from_path") as mock_convert:
        mock_image = MagicMock()
        mock_convert.return_value = [mock_image]
        yield mock_convert


def test_ocr_engine_init(mock_ollama_client):
    engine = OCREngine(host="http://mock-host", user="user", password="password")
    assert engine.host == "http://mock-host"
    assert engine.user == "user"
    assert engine.password == "password"
    assert engine.model == "qwen3.5:9b"
    assert engine.dpi == 300


def test_count_pdf_pages(mock_pdf_reader):
    engine = OCREngine()
    with patch("builtins.open", mock_open(read_data=b"dummy")):
        pages = engine.count_pdf_pages(Path("dummy.pdf"))
    assert pages == 2


def test_ocr_single_page_success(mock_ollama_client):
    engine = OCREngine()
    # Mock Ollama Client response
    mock_response = MagicMock()
    mock_response.message = {"content": "Transcription content"}
    mock_ollama_client.chat.return_value = mock_response

    transcription = engine.ocr_single_page(
        image_path=Path("dummy.png"), last_text="previous page text"
    )
    assert transcription == "Transcription content"
    mock_ollama_client.chat.assert_called_once()


@pytest.mark.parametrize("mode", ["standard", "glm", "firered"])
def test_plain_response_crosses_normalization_boundary_unchanged(
    mock_ollama_client, ocr_response_factory, mode
):
    content = "Plain OCR text\nwith meaningful spacing  \n"
    mock_ollama_client.chat.return_value = ocr_response_factory(content)

    assert normalize_ocr_response(content) == content
    assert OCREngine(mode=mode).ocr_single_page(Path("page.png")) == content


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("reasoning</think>Recognized page", "Recognized page"),
        ("</think>Recognized page", "Recognized page"),
        ("reasoning</think>", ""),
        ("first</think>still reasoning</think>Final OCR", "Final OCR"),
        ("reasoning</think>\n\n  \nRecognized page", "Recognized page"),
        ("reasoning</THINK>Recognized page", "reasoning</THINK>Recognized page"),
        ("No reasoning marker", "No reasoning marker"),
    ],
)
def test_normalize_ocr_response_removes_content_through_final_think_marker(content, expected):
    assert normalize_ocr_response(content) == expected


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        (
            "    First line\n        Nested line\n    Final line\n",
            "First line\n    Nested line\nFinal line\n",
        ),
        ("Unindented\n    Nested\n", "Unindented\n    Nested\n"),
        ("    First\n  \n        Nested\n", "First\n  \n    Nested\n"),
        ("    First\n\tNested\n", "    First\n\tNested\n"),
        ("    First\n    \tNested\n", "    First\n    \tNested\n"),
        ("", ""),
        ("  \n\n", "  \n\n"),
        (
            "    First\r\n        Nested\r\n    Final\r\n",
            "First\r\n    Nested\r\nFinal\r\n",
        ),
        ("    Single line\n", "Single line\n"),
        (
            "reasoning</think>\n\n    First\n        Nested\n",
            "First\n    Nested\n",
        ),
    ],
)
def test_normalize_ocr_response_removes_only_shared_ascii_space_margin(content, expected):
    assert normalize_ocr_response(content) == expected


def test_standard_next_page_context_uses_normalized_previous_response(
    mock_pdf_reader,
    mock_convert_from_path,
    mock_ollama_client,
    ocr_response_factory,
):
    engine = OCREngine(mode="standard")
    mock_ollama_client.chat.side_effect = [
        ocr_response_factory("SECRET REASONING</think>PAGE ONE OCR"),
        ocr_response_factory("PAGE TWO OCR"),
    ]

    with (
        patch("builtins.open", mock_open(read_data=b"dummy")),
        patch("pathlib.Path.unlink"),
    ):
        engine.run_ocr(Path("dummy.pdf"))

    second_messages = mock_ollama_client.chat.call_args_list[1].kwargs["messages"]
    assert "PAGE ONE OCR" in str(second_messages)
    assert "SECRET REASONING" not in str(second_messages)
    assert "</think>" not in str(second_messages)


def test_ocr_single_page_retry_success(mock_ollama_client):
    engine = OCREngine()
    mock_response = MagicMock()
    mock_response.message = {"content": "Successful after retry"}

    # Fail once, then succeed
    mock_ollama_client.chat.side_effect = [Exception("Temporary error"), mock_response]

    transcription = engine.ocr_single_page(
        image_path=Path("dummy.png"), retry=2, retry_backoff=0.01
    )
    assert transcription == "Successful after retry"
    assert mock_ollama_client.chat.call_count == 2


def test_run_ocr(mock_pdf_reader, mock_convert_from_path, mock_ollama_client):
    engine = OCREngine()
    mock_response = MagicMock()
    mock_response.message = {"content": "Page content here"}
    mock_ollama_client.chat.return_value = mock_response

    with (
        patch("builtins.open", mock_open(read_data=b"dummy")),
        patch("pathlib.Path.unlink"),
    ):
        result = engine.run_ocr(
            input_pdf=Path("dummy.pdf"),
            page_header=True,
        )

        assert "Page 1" in result
        assert "Page 2" in result
        assert result.index("Page 1") < result.index("Page 2")
        assert "Page content here" in result
        assert mock_ollama_client.chat.call_count == 2


def test_run_ocr_resume(mock_pdf_reader, mock_convert_from_path, mock_ollama_client, tmp_path):
    engine = OCREngine()

    # Pre-create output md with page 1 already recognized
    output_md = tmp_path / "output.md"
    output_md.write_text("---\n\n# Page 1\n\nExisting content of page 1\n")

    mock_response = MagicMock()
    mock_response.message = {"content": "Page 2 content"}
    mock_ollama_client.chat.return_value = mock_response

    with (
        patch("builtins.open", mock_open(read_data=b"dummy")),
        patch("pathlib.Path.unlink"),
    ):
        engine.run_ocr(
            input_pdf=Path("dummy.pdf"),
            output_md=output_md,
            page_header=True,
        )

        # Chat should only be called once (for page 2), because page 1 is skipped
        assert mock_ollama_client.chat.call_count == 1

        # Verify call context contains previous page content
        call_args = mock_ollama_client.chat.call_args[1]
        user_message = call_args["messages"][-1]["content"]
        assert (
            "For OCR context, previous transcribed page was: Existing content of page 1"
            in user_message
        )

        # Verify output contains both pages
        output_content = output_md.read_text()
        assert "Page 1" in output_content
        assert "Existing content of page 1" in output_content
        assert "Page 2" in output_content
        assert "Page 2 content" in output_content


def test_run_ocr_logs_average_for_distinct_attempted_pages(
    mock_pdf_reader, mock_convert_from_path, mock_ollama_client, ocr_response_factory
):
    engine = OCREngine()
    mock_ollama_client.chat.return_value = ocr_response_factory("Page text")

    with (
        patch("builtins.open", mock_open(read_data=b"dummy")),
        patch("pathlib.Path.unlink"),
        patch("archivatorium.ocr_engine.time.perf_counter", side_effect=[10.0, 20.0]),
        patch("archivatorium.ocr_engine.logger.info") as mock_logger,
    ):
        engine.run_ocr(Path("dummy.pdf"))

    assert_ocr_timing_log(
        mock_logger,
        attempted_pages=2,
        total_seconds=10.0,
        average_seconds_per_page=5.0,
    )


def test_run_ocr_retry_counts_page_once_and_includes_retry_time(
    mock_convert_from_path, mock_ollama_client, ocr_response_factory
):
    engine = OCREngine()
    mock_ollama_client.chat.side_effect = [
        RuntimeError("temporary"),
        ocr_response_factory("Recovered"),
    ]

    with (
        patch.object(engine, "count_pdf_pages", return_value=1),
        patch("pathlib.Path.unlink"),
        patch("archivatorium.ocr_engine.time.sleep"),
        patch("archivatorium.ocr_engine.time.perf_counter", side_effect=[2.0, 11.0]),
        patch("archivatorium.ocr_engine.logger.info") as mock_logger,
    ):
        engine.run_ocr(Path("dummy.pdf"))

    assert mock_ollama_client.chat.call_count == 2
    assert_ocr_timing_log(
        mock_logger,
        attempted_pages=1,
        total_seconds=9.0,
        average_seconds_per_page=9.0,
    )


def test_run_ocr_logs_timing_when_page_processing_fails():
    engine = OCREngine()

    with (
        patch.object(engine, "count_pdf_pages", return_value=1),
        patch.object(
            engine,
            "render_pdf_page_to_png",
            side_effect=RuntimeError("render failed"),
        ),
        patch("archivatorium.ocr_engine.time.perf_counter", side_effect=[3.0, 7.5]),
        patch("archivatorium.ocr_engine.logger.info") as mock_logger,
        pytest.raises(RuntimeError, match="render failed"),
    ):
        engine.run_ocr(Path("dummy.pdf"))

    assert_ocr_timing_log(
        mock_logger,
        attempted_pages=1,
        total_seconds=4.5,
        average_seconds_per_page=4.5,
    )


def test_run_ocr_resume_excludes_skipped_page_from_attempt_count(
    mock_pdf_reader,
    mock_convert_from_path,
    mock_ollama_client,
    ocr_response_factory,
    tmp_path,
):
    engine = OCREngine()
    output_md = tmp_path / "output.md"
    output_md.write_text("---\n\n# Page 1\n\nExisting page\n", encoding="utf-8")
    mock_ollama_client.chat.return_value = ocr_response_factory("New page")

    with (
        patch("builtins.open", mock_open(read_data=b"dummy")),
        patch("pathlib.Path.unlink"),
        patch("archivatorium.ocr_engine.time.perf_counter", side_effect=[1.0, 5.0]),
        patch("archivatorium.ocr_engine.logger.info") as mock_logger,
    ):
        engine.run_ocr(Path("dummy.pdf"), output_md=output_md)

    assert_ocr_timing_log(
        mock_logger,
        attempted_pages=1,
        total_seconds=4.0,
        average_seconds_per_page=4.0,
    )


def test_run_ocr_zero_pages_logs_unavailable_average():
    engine = OCREngine()

    with (
        patch.object(engine, "count_pdf_pages", return_value=0),
        patch("archivatorium.ocr_engine.time.perf_counter", side_effect=[4.0, 4.25]),
        patch("archivatorium.ocr_engine.logger.info") as mock_logger,
    ):
        assert engine.run_ocr(Path("empty.pdf")) == ""

    assert_ocr_timing_log(
        mock_logger,
        attempted_pages=0,
        total_seconds=0.25,
        average_seconds_per_page=None,
    )


def test_glm_single_page_uses_native_isolated_request(
    mock_ollama_client, ocr_response_factory, ocr_call_kwargs
):
    engine = OCREngine(mode="glm")
    mock_ollama_client.chat.return_value = ocr_response_factory("GLM text")

    transcription = engine.ocr_single_page(
        image_path=Path("page.png"),
        last_text="SECRET PREVIOUS PAGE",
    )

    assert transcription == "GLM text"
    kwargs = ocr_call_kwargs(mock_ollama_client)
    assert kwargs == {
        "model": "qwen3.5:9b",
        "messages": [
            {
                "role": "user",
                "content": "Text Recognition:",
                "images": ["page.png"],
            }
        ],
        "options": GLM_DEFAULT_OPTIONS,
        "stream": False,
        "think": False,
    }


def test_glm_retry_reuses_identical_isolated_request(mock_ollama_client, ocr_response_factory):
    engine = OCREngine(mode="glm")
    mock_ollama_client.chat.side_effect = [
        RuntimeError("temporary"),
        ocr_response_factory("Recovered"),
    ]

    with patch("archivatorium.ocr_engine.time.sleep"):
        assert (
            engine.ocr_single_page(
                image_path=Path("page.png"),
                last_text="SECRET PREVIOUS PAGE",
                retry=2,
            )
            == "Recovered"
        )

    first = mock_ollama_client.chat.call_args_list[0].kwargs
    second = mock_ollama_client.chat.call_args_list[1].kwargs
    assert first == second
    assert first["think"] is False
    assert "SECRET PREVIOUS PAGE" not in str(first["messages"])


def test_glm_multipage_requests_do_not_share_recognized_text(
    mock_pdf_reader,
    mock_convert_from_path,
    mock_ollama_client,
    ocr_response_factory,
):
    engine = OCREngine(mode="glm")
    mock_ollama_client.chat.side_effect = [
        ocr_response_factory("FIRST PAGE SECRET"),
        ocr_response_factory("SECOND PAGE"),
    ]

    with (
        patch("builtins.open", mock_open(read_data=b"dummy")),
        patch("pathlib.Path.unlink"),
    ):
        engine.run_ocr(input_pdf=Path("dummy.pdf"))

    assert mock_ollama_client.chat.call_count == 2
    second_messages = mock_ollama_client.chat.call_args_list[1].kwargs["messages"]
    assert "FIRST PAGE SECRET" not in str(second_messages)
    assert second_messages[0]["content"] == "Text Recognition:"


def test_glm_resume_does_not_send_existing_neighbor_text(
    mock_pdf_reader,
    mock_convert_from_path,
    mock_ollama_client,
    ocr_response_factory,
    tmp_path,
):
    engine = OCREngine(mode="glm")
    output_md = tmp_path / "output.md"
    output_md.write_text(
        "---\n\n# Page 1\n\nEXISTING PAGE SECRET\n",
        encoding="utf-8",
    )
    mock_ollama_client.chat.return_value = ocr_response_factory("Page 2")

    with (
        patch("builtins.open", mock_open(read_data=b"dummy")),
        patch("pathlib.Path.unlink"),
    ):
        engine.run_ocr(
            input_pdf=Path("dummy.pdf"),
            output_md=output_md,
        )

    assert mock_ollama_client.chat.call_count == 1
    kwargs = mock_ollama_client.chat.call_args.kwargs
    assert "EXISTING PAGE SECRET" not in str(kwargs["messages"])
    assert kwargs["think"] is False


def test_firered_single_page_uses_exact_isolated_request(
    mock_ollama_client, ocr_response_factory, ocr_call_kwargs
):
    engine = OCREngine(mode="firered", model="remote/firered-ocr:latest")
    mock_ollama_client.chat.return_value = ocr_response_factory("FireRed text")

    assert FIRERED_USER_PROMPT == FIRERED_EXPECTED_PROMPT
    assert (
        engine.ocr_single_page(
            image_path=Path("page.png"),
            last_text="SECRET PREVIOUS PAGE",
        )
        == "FireRed text"
    )

    assert ocr_call_kwargs(mock_ollama_client) == {
        "model": "remote/firered-ocr:latest",
        "messages": [
            {
                "role": "user",
                "content": FIRERED_EXPECTED_PROMPT,
                "images": ["page.png"],
            }
        ],
        "options": {"num_ctx": 8192, "num_predict": 4096 * 4},
        "stream": False,
    }


def test_firered_retry_reuses_identical_isolated_request(mock_ollama_client, ocr_response_factory):
    engine = OCREngine(mode="firered")
    mock_ollama_client.chat.side_effect = [
        RuntimeError("temporary"),
        ocr_response_factory("Recovered"),
    ]

    with patch("archivatorium.ocr_engine.time.sleep"):
        assert (
            engine.ocr_single_page(
                image_path=Path("page.png"),
                last_text="SECRET PREVIOUS PAGE",
                retry=2,
            )
            == "Recovered"
        )

    first = mock_ollama_client.chat.call_args_list[0].kwargs
    second = mock_ollama_client.chat.call_args_list[1].kwargs
    assert first == second
    assert "SECRET PREVIOUS PAGE" not in str(first["messages"])
    assert "think" not in first


def test_firered_multipage_requests_do_not_share_recognized_text(
    mock_pdf_reader,
    mock_convert_from_path,
    mock_ollama_client,
    ocr_response_factory,
):
    engine = OCREngine(mode="firered")
    mock_ollama_client.chat.side_effect = [
        ocr_response_factory("FIRST PAGE SECRET"),
        ocr_response_factory("SECOND PAGE"),
    ]

    with (
        patch("builtins.open", mock_open(read_data=b"dummy")),
        patch("pathlib.Path.unlink"),
    ):
        engine.run_ocr(input_pdf=Path("dummy.pdf"))

    second_messages = mock_ollama_client.chat.call_args_list[1].kwargs["messages"]
    assert "FIRST PAGE SECRET" not in str(second_messages)
    assert second_messages[0]["content"] == FIRERED_EXPECTED_PROMPT


def test_firered_resume_does_not_send_existing_neighbor_text(
    mock_pdf_reader,
    mock_convert_from_path,
    mock_ollama_client,
    ocr_response_factory,
    tmp_path,
):
    engine = OCREngine(mode="firered")
    output_md = tmp_path / "output.md"
    output_md.write_text(
        "---\n\n# Page 1\n\nEXISTING PAGE SECRET\n",
        encoding="utf-8",
    )
    mock_ollama_client.chat.return_value = ocr_response_factory("Page 2")

    with (
        patch("builtins.open", mock_open(read_data=b"dummy")),
        patch("pathlib.Path.unlink"),
    ):
        engine.run_ocr(input_pdf=Path("dummy.pdf"), output_md=output_md)

    kwargs = mock_ollama_client.chat.call_args.kwargs
    assert "EXISTING PAGE SECRET" not in str(kwargs["messages"])
    assert kwargs["messages"][0]["content"] == FIRERED_EXPECTED_PROMPT
    assert "think" not in kwargs


def test_standard_request_preserves_exact_existing_shape(
    mock_ollama_client, ocr_response_factory, ocr_call_kwargs
):
    engine = OCREngine(mode="standard")
    mock_ollama_client.chat.return_value = ocr_response_factory("Standard text")

    assert (
        engine.ocr_single_page(
            image_path=Path("page.png"),
            last_text="PREVIOUS STANDARD PAGE",
        )
        == "Standard text"
    )

    kwargs = ocr_call_kwargs(mock_ollama_client)
    assert kwargs == {
        "model": "qwen3.5:9b",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    USER_PROMPT + "\n\nFor OCR context, previous transcribed page was: "
                    "PREVIOUS STANDARD PAGE"
                ),
                "images": ["page.png"],
            },
        ],
        "options": {"num_ctx": 8192, "num_predict": 4096 * 4},
        "stream": False,
    }
    assert "think" not in kwargs


def test_omitted_and_explicit_standard_modes_are_identical(
    mock_ollama_client, ocr_response_factory
):
    mock_ollama_client.chat.return_value = ocr_response_factory("Standard text")
    default_engine = OCREngine()
    explicit_engine = OCREngine(mode="standard")

    default_engine.ocr_single_page(Path("page.png"), last_text="previous")
    explicit_engine.ocr_single_page(Path("page.png"), last_text="previous")

    first = mock_ollama_client.chat.call_args_list[0].kwargs
    second = mock_ollama_client.chat.call_args_list[1].kwargs
    assert first == second


def test_standard_retry_keeps_context_and_request_shape(mock_ollama_client, ocr_response_factory):
    engine = OCREngine(mode="standard")
    mock_ollama_client.chat.side_effect = [
        RuntimeError("temporary"),
        ocr_response_factory("Recovered"),
    ]

    with patch("archivatorium.ocr_engine.time.sleep"):
        engine.ocr_single_page(
            Path("page.png"),
            last_text="STANDARD CONTEXT",
            retry=2,
        )

    first = mock_ollama_client.chat.call_args_list[0].kwargs
    second = mock_ollama_client.chat.call_args_list[1].kwargs
    assert first == second
    assert "STANDARD CONTEXT" in first["messages"][-1]["content"]
    assert "think" not in first


@pytest.mark.parametrize("model", ["qwen3.5:9b", "remote/custom-glm:latest"])
def test_glm_profile_never_selects_or_replaces_model(
    mock_ollama_client, ocr_response_factory, model
):
    engine = OCREngine(mode="glm", model=model)
    mock_ollama_client.chat.return_value = ocr_response_factory("Text")

    engine.ocr_single_page(Path("page.png"))

    assert not hasattr(engine.profile, "model")
    assert engine.model == model
    assert mock_ollama_client.chat.call_args.kwargs["model"] == model
    assert mock_ollama_client.chat.call_args.kwargs["think"] is False


@pytest.mark.parametrize(
    ("option", "value"),
    [
        ("temperature", 0.25),
        ("top_p", 0.5),
        ("top_k", 7),
        ("repeat_penalty", 1.25),
        ("repeat_last_n", 1024),
        ("num_predict", 4096),
    ],
)
def test_glm_single_inference_override_changes_only_matching_default(
    mock_ollama_client, ocr_response_factory, option, value
):
    engine = OCREngine(mode="glm", **{option: value})
    mock_ollama_client.chat.return_value = ocr_response_factory("Text")

    engine.ocr_single_page(Path("page.png"))

    expected = {**GLM_DEFAULT_OPTIONS, option: value}
    assert mock_ollama_client.chat.call_args.kwargs["options"] == expected


def test_glm_all_inference_overrides_and_zero_values_are_preserved(
    mock_ollama_client, ocr_response_factory
):
    engine = OCREngine(
        mode="glm",
        temperature=0.0,
        top_p=0.0,
        top_k=0,
        repeat_penalty=1.2,
        repeat_last_n=-1,
        num_predict=-1,
    )
    mock_ollama_client.chat.return_value = ocr_response_factory("Text")

    engine.ocr_single_page(Path("page.png"))

    assert mock_ollama_client.chat.call_args.kwargs["options"] == {
        "num_ctx": 8192,
        "temperature": 0.0,
        "top_p": 0.0,
        "top_k": 0,
        "repeat_penalty": 1.2,
        "repeat_last_n": -1,
        "num_predict": -1,
    }


def test_standard_mode_allows_explicit_inference_tuning(mock_ollama_client, ocr_response_factory):
    engine = OCREngine(mode="standard", temperature=0.0, repeat_last_n=0, num_predict=2048)
    mock_ollama_client.chat.return_value = ocr_response_factory("Text")

    engine.ocr_single_page(Path("page.png"), last_text="context")

    kwargs = mock_ollama_client.chat.call_args.kwargs
    assert kwargs["options"] == {
        "num_ctx": 8192,
        "num_predict": 2048,
        "temperature": 0.0,
        "repeat_last_n": 0,
    }
    assert kwargs["messages"][0]["role"] == "system"
    assert "context" in kwargs["messages"][-1]["content"]
    assert "think" not in kwargs


@pytest.mark.parametrize(
    ("option", "value", "message"),
    [
        ("temperature", -0.1, "temperature"),
        ("top_p", -0.1, "top_p"),
        ("top_p", 1.1, "top_p"),
        ("top_k", -1, "top_k"),
        ("repeat_penalty", 0.0, "repeat_penalty"),
        ("repeat_last_n", -2, "repeat_last_n"),
        ("num_predict", 0, "num_predict"),
        ("num_predict", -2, "num_predict"),
    ],
)
def test_invalid_programmatic_inference_values_are_rejected(option, value, message):
    with pytest.raises(ValueError, match=message):
        OCREngine(**{option: value})
