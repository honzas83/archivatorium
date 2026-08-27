from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

import pytest
from archivatorium.ocr_engine import FIRERED_USER_PROMPT, OCREngine, SYSTEM_PROMPT, USER_PROMPT


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
