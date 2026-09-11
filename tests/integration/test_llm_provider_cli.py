from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from archivatorium.cli import cli
from archivatorium.models.metadata import MetadataSchema, WindowTaggingResult
from archivatorium.services.llm_client import (
    CompletionState,
    LLMClient,
    LLMError,
    LLMErrorCategory,
    ModelRequest,
    ModelResponse,
)


def test_metadata_exposes_common_provider_options() -> None:
    result = CliRunner().invoke(cli, ["metadata", "--help"])

    assert result.exit_code == 0
    assert "--llm-provider" in result.output
    assert "--llm-base-url" in result.output
    assert "--llm-api-key-file" in result.output
    assert "--host" in result.output


def _metadata_args(tmp_path: Path) -> list[str]:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    hierarchy = tmp_path / "hierarchy.yaml"
    hierarchy.write_text(
        """categories:
  - category: Archive
    description: Archival subjects
    topics:
      - topic: Administration
        description: Administrative matters
        positive_samples: substantive administration
        negative_samples: incidental mention
""",
        encoding="utf-8",
    )
    tags = tmp_path / "tags.yaml"
    tags.write_text("useful_tags: []\n", encoding="utf-8")
    return [
        "metadata",
        str(input_dir),
        str(tmp_path / "output"),
        "--hierarchy-file",
        str(hierarchy),
        "--tags-file",
        str(tags),
    ]


def test_einfra_metadata_defaults_and_environment_credential(tmp_path: Path) -> None:
    fake_client = MagicMock(spec=LLMClient)
    with (
        patch("archivatorium.cli.build_llm_client", return_value=fake_client) as build,
        patch("archivatorium.cli.MetadataProcessor") as processor,
        patch("archivatorium.cli.TaggingService"),
    ):
        processor.return_value.get_files.return_value = []
        result = CliRunner().invoke(
            cli,
            _metadata_args(tmp_path) + ["--llm-provider", "e-infra"],
            env={"E_INFRA_API_TOKEN": "secret"},
        )

    assert result.exit_code == 0, result.output
    connection = build.call_args.args[0]
    assert connection.provider == "e-infra"
    assert connection.endpoint == "https://llm.ai.e-infra.cz/v1/"
    assert connection.model == "qwen3.8-27b"


def test_einfra_missing_credential_fails_before_output_or_processing(tmp_path: Path) -> None:
    args = _metadata_args(tmp_path) + ["--llm-provider", "e-infra"]
    with (
        patch("archivatorium.cli.MetadataProcessor") as processor,
        patch("archivatorium.cli.initialize_vault_from_template") as initialize,
    ):
        result = CliRunner().invoke(
            cli,
            args,
            env={"E_INFRA_API_TOKEN": "", "OPENAI_API_KEY": "must-not-be-used"},
        )

    assert result.exit_code == 2
    assert "E_INFRA_API_TOKEN" in result.output
    processor.assert_not_called()
    initialize.assert_not_called()
    assert not (tmp_path / "output").exists()


def test_endpoint_alias_conflict_fails_before_processing(tmp_path: Path) -> None:
    args = _metadata_args(tmp_path) + [
        "--llm-base-url",
        "http://one.test",
        "--host",
        "http://two.test",
    ]
    with patch("archivatorium.cli.MetadataProcessor") as processor:
        result = CliRunner().invoke(cli, args)

    assert result.exit_code == 2
    assert "conflicting" in result.output.lower()
    processor.assert_not_called()


class _StructuredFake:
    def __init__(self, failure: LLMError | None = None) -> None:
        self.failure = failure
        self.calls: list[tuple[type[object], dict[str, object]]] = []

    def extract_structured(self, _prompt, schema, **kwargs):
        self.calls.append((schema, kwargs))
        if self.failure is not None:
            raise self.failure
        if schema is MetadataSchema:
            return MetadataSchema(title="Remote Title", summary="Remote summary.")
        return WindowTaggingResult()


def test_einfra_metadata_and_tagging_keep_existing_output_contract(tmp_path: Path) -> None:
    args = _metadata_args(tmp_path) + [
        "--llm-provider",
        "e-infra",
        "--model-think",
        "low",
    ]
    input_file = tmp_path / "input" / "document.md"
    input_file.write_text("Cancelled.", encoding="utf-8")
    fake = _StructuredFake()

    with patch("archivatorium.cli.build_llm_client", return_value=fake):
        result = CliRunner().invoke(cli, args, env={"E_INFRA_API_TOKEN": "synthetic-token"})

    assert result.exit_code == 0, result.output
    saved = (tmp_path / "output" / "document.md").read_text(encoding="utf-8")
    assert saved.startswith("---\n")
    assert "title: Remote Title" in saved
    assert "provider:" not in saved
    assert "reasoning" not in saved.lower()
    assert [call[1]["think"] for call in fake.calls] == ["low", "low"]
    assert fake.calls[1][1]["model"] == "qwen3.8-27b"


def test_per_document_einfra_failure_does_not_fallback_or_write_output(tmp_path: Path) -> None:
    args = _metadata_args(tmp_path) + ["--llm-provider", "e-infra"]
    (tmp_path / "input" / "document.md").write_text("Source", encoding="utf-8")
    failure = LLMError(
        LLMErrorCategory.AUTHENTICATION,
        "e-INFRA authentication failed",
        retryable=False,
    )
    fake = _StructuredFake(failure)

    with (
        patch("archivatorium.cli.build_llm_client", return_value=fake) as build,
        patch("archivatorium.cli.OllamaClient") as ollama,
    ):
        result = CliRunner().invoke(cli, args, env={"E_INFRA_API_TOKEN": "synthetic-token"})

    assert result.exit_code == 0
    assert not (tmp_path / "output" / "document.md").exists()
    build.assert_called_once()
    ollama.assert_not_called()


def _ocr_args(tmp_path: Path) -> list[str]:
    input_dir = tmp_path / "pdf-input"
    input_dir.mkdir()
    return ["ocr", str(input_dir), str(tmp_path / "ocr-output")]


def test_ocr_exposes_common_provider_options() -> None:
    result = CliRunner().invoke(cli, ["ocr", "--help"])

    assert result.exit_code == 0
    assert "--llm-provider" in result.output
    assert "--llm-base-url" in result.output
    assert "--llm-api-key-file" in result.output
    assert "--host" in result.output


def test_einfra_ocr_uses_remote_defaults_and_one_injected_client(tmp_path: Path) -> None:
    fake_client = MagicMock(spec=LLMClient)
    with (
        patch("archivatorium.cli.build_llm_client", return_value=fake_client) as build,
        patch("archivatorium.ocr_engine.OCREngine") as engine,
    ):
        result = CliRunner().invoke(
            cli,
            _ocr_args(tmp_path) + ["--llm-provider", "e-infra", "--mode", "qwen38"],
            env={"E_INFRA_API_TOKEN": "synthetic-token"},
        )

    assert result.exit_code == 0, result.output
    connection = build.call_args.args[0]
    assert connection.model == "qwen3.8-27b"
    assert connection.endpoint == "https://llm.ai.e-infra.cz/v1/"
    assert engine.call_args.kwargs["model"] == "qwen3.8-27b"
    assert engine.call_args.kwargs["llm_client"] is fake_client


@pytest.mark.parametrize(
    "options",
    [
        ["--mode", "glm"],
        ["--mode", "qwen38", "--top-k", "1"],
        ["--mode", "qwen38", "--repeat-penalty", "1.1"],
        ["--mode", "qwen38", "--repeat-last-n", "10"],
        ["--mode", "qwen38", "--num-predict", "-1"],
        ["--mode", "qwen38", "--user", "digest"],
        ["--mode", "qwen38", "--password", "digest"],
    ],
)
def test_invalid_einfra_ocr_configuration_fails_before_discovery(
    tmp_path: Path, options: list[str]
) -> None:
    with patch("archivatorium.ocr_engine.OCREngine") as engine:
        result = CliRunner().invoke(
            cli,
            _ocr_args(tmp_path) + ["--llm-provider", "e-infra", *options],
            env={"E_INFRA_API_TOKEN": "synthetic-token"},
        )

    assert result.exit_code == 2
    engine.assert_not_called()


class _TextFake:
    provider = "e-infra"

    def __init__(self, responses: list[str]) -> None:
        self.responses = iter(responses)
        self.requests: list[ModelRequest] = []

    def generate_text(self, request: ModelRequest) -> ModelResponse:
        self.requests.append(request)
        return ModelResponse(
            visible_text=next(self.responses),
            finish_state=CompletionState.COMPLETE,
        )


def test_einfra_multipage_ocr_preserves_layout_context_and_resume(tmp_path: Path) -> None:
    args = _ocr_args(tmp_path) + ["--llm-provider", "e-infra", "--mode", "qwen38"]
    (tmp_path / "pdf-input" / "document.pdf").write_bytes(b"synthetic pdf")
    fake = _TextFake(["PAGE ONE", "PAGE TWO"])

    with (
        patch("archivatorium.cli.build_llm_client", return_value=fake),
        patch("archivatorium.ocr_engine.PdfReader") as reader,
        patch("archivatorium.ocr_engine.convert_from_path") as convert,
    ):
        reader.return_value.pages = [MagicMock(), MagicMock()]
        convert.return_value = [MagicMock()]
        first = CliRunner().invoke(cli, args, env={"E_INFRA_API_TOKEN": "synthetic-token"})
        second = CliRunner().invoke(cli, args, env={"E_INFRA_API_TOKEN": "synthetic-token"})

    assert first.exit_code == 0, first.output
    assert second.exit_code == 0, second.output
    assert len(fake.requests) == 2
    assert all(request.delivery == "incremental" for request in fake.requests)
    assert "PAGE ONE" in fake.requests[1].messages[-1].text
    saved = (tmp_path / "ocr-output" / "document.md").read_text(encoding="utf-8")
    assert saved == "---\n\n# Page 1\n\nPAGE ONE\n\n---\n\n# Page 2\n\nPAGE TWO"
