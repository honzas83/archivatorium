from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from archivatorium.cli import cli
from archivatorium.models.metadata import LastDateSchema, MetadataSchema
from archivatorium.utils.metadata import parse_frontmatter
from tests.unit.test_ollama_client import create_mock_ollama_response


@pytest.fixture
def temp_dirs(tmp_path: Path) -> tuple[Path, Path]:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    # Create a dummy markdown file
    md_file = input_dir / "test.md"
    md_file.write_text("This is a test document.")

    return input_dir, output_dir


def test_metadata_command_requires_taxonomy_files(temp_dirs: tuple[Path, Path]) -> None:
    input_dir, output_dir = temp_dirs
    runner = CliRunner()

    missing_hierarchy = runner.invoke(cli, ["metadata", str(input_dir), str(output_dir)])
    assert missing_hierarchy.exit_code != 0
    assert "Missing option '--hierarchy-file'" in missing_hierarchy.output


def test_metadata_command_requires_tags_file(
    temp_dirs: tuple[Path, Path], hierarchy_file: Path
) -> None:
    input_dir, output_dir = temp_dirs
    runner = CliRunner()

    result = runner.invoke(
        cli, ["metadata", str(input_dir), str(output_dir), "--hierarchy-file", str(hierarchy_file)]
    )
    assert result.exit_code != 0
    assert "Missing option '--tags-file'" in result.output


def test_metadata_command_basic(
    temp_dirs: tuple[Path, Path], hierarchy_file: Path, useful_tags_file: Path
) -> None:
    input_dir, output_dir = temp_dirs
    runner = CliRunner()

    mock_metadata = {
        "title": "Test Title",
        "author_name": "Test Author",
        "language": "English",
        "date": "1981-11-19",
    }

    with (
        patch("ollama.Client.chat") as mock_chat,
        patch("archivatorium.services.tagging_service.TaggingService.extract_tags"),
    ):
        mock_chat.return_value = create_mock_ollama_response(
            MetadataSchema(**mock_metadata).model_dump_json()
        )

        result = runner.invoke(
            cli,
            [
                "metadata",
                str(input_dir),
                str(output_dir),
                "--hierarchy-file",
                str(hierarchy_file),
                "--tags-file",
                str(useful_tags_file),
            ],
        )

        assert result.exit_code == 0


def test_metadata_command_with_host(
    temp_dirs: tuple[Path, Path], hierarchy_file: Path, useful_tags_file: Path
) -> None:
    input_dir, output_dir = temp_dirs
    runner = CliRunner()

    with (
        patch("archivatorium.cli.OllamaClient") as mock_client_class,
        patch("archivatorium.services.tagging_service.TaggingService.extract_tags"),
    ):
        result = runner.invoke(
            cli,
            [
                "metadata",
                str(input_dir),
                str(output_dir),
                "--hierarchy-file",
                str(hierarchy_file),
                "--tags-file",
                str(useful_tags_file),
                "--host",
                "http://custom-ollama-host:11434",
            ],
        )

        assert result.exit_code == 0
        mock_client_class.assert_called_once_with(model="gemma4:31b", host="http://custom-ollama-host:11434")


def test_metadata_command_outputs_leading_item_type(
    temp_dirs: tuple[Path, Path], hierarchy_file: Path, useful_tags_file: Path
) -> None:
    input_dir, output_dir = temp_dirs
    runner = CliRunner()

    mock_metadata = {
        "item_type": "correspondence",
        "title": "Test Letter",
        "summary": "A test correspondence item.",
        "language": "English",
    }

    with (
        patch("ollama.Client.chat") as mock_chat,
        patch("archivatorium.services.tagging_service.TaggingService.extract_tags"),
    ):
        mock_chat.return_value = create_mock_ollama_response(
            MetadataSchema(**mock_metadata).model_dump_json()
        )

        result = runner.invoke(
            cli,
            [
                "metadata",
                str(input_dir),
                str(output_dir),
                "--hierarchy-file",
                str(hierarchy_file),
                "--tags-file",
                str(useful_tags_file),
            ],
        )

    assert result.exit_code == 0
    output_content = (output_dir / "test.md").read_text()
    metadata, _ = parse_frontmatter(output_content)
    assert list(metadata.keys())[:2] == ["item_type", "title"]
    assert metadata["item_type"] == "correspondence"


def test_metadata_command_no_non_flat_topic_mode() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["metadata", "--help"])

    assert result.exit_code == 0
    assert "--flat-topics" not in result.output


def test_metadata_command_large_file_date_fallback(
    temp_dirs: tuple[Path, Path], hierarchy_file: Path, useful_tags_file: Path
) -> None:
    input_dir, output_dir = temp_dirs
    runner = CliRunner()

    # Create a large file (> 12000 chars)
    large_file = input_dir / "large.md"
    content = (
        "Start of document without clear date. "
        + ("x" * 15000)
        + " End of document. Final Date: 2026-12-31."
    )
    large_file.write_text(content)

    with (
        patch("ollama.Client.chat") as mock_chat,
        patch("archivatorium.services.tagging_service.TaggingService.extract_tags"),
    ):
        # Mock first pass (MetadataSchema) - missing date
        data1 = {"language": "English", "title": "Large Doc"}
        resp1 = create_mock_ollama_response(MetadataSchema(**data1).model_dump_json())

        # Mock second pass (LastDateSchema) - finds date
        data2 = {"date": "2026-12-31"}
        resp2 = create_mock_ollama_response(LastDateSchema(**data2).model_dump_json())

        mock_chat.side_effect = [resp1, resp2]

        result = runner.invoke(
            cli,
            [
                "metadata",
                str(input_dir),
                str(output_dir),
                "--hierarchy-file",
                str(hierarchy_file),
                "--tags-file",
                str(useful_tags_file),
            ],
        )

        assert result.exit_code == 0

        output_file = output_dir / "large.md"
        assert output_file.exists()
        output_content = output_file.read_text()

        # Verify date was updated from the second pass
        assert "date: '2026-12-31'" in output_content or "date: 2026-12-31" in output_content


def test_metadata_mask_enriches_only_matching_markdown(
    tmp_path: Path, hierarchy_file: Path, useful_tags_file: Path
) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    (input_dir / "match.md").write_text("matching")
    (input_dir / "skip.txt.md").write_text("nonmatching")

    runner = CliRunner()
    with (
        patch("ollama.Client.chat") as mock_chat,
        patch("archivatorium.services.tagging_service.TaggingService.extract_tags"),
    ):
        mock_chat.return_value = create_mock_ollama_response(
            MetadataSchema(title="Matched").model_dump_json()
        )
        result = runner.invoke(
            cli,
            [
                "metadata",
                str(input_dir),
                str(output_dir),
                "--mask",
                "match.md",
                "--hierarchy-file",
                str(hierarchy_file),
                "--tags-file",
                str(useful_tags_file),
            ],
        )

    assert result.exit_code == 0
    assert mock_chat.call_count == 1
    assert (output_dir / "match.md").read_text().startswith("---")
    assert (output_dir / "skip.txt.md").read_text() == "nonmatching"


def test_metadata_filtered_sidecar_is_not_enriched(
    tmp_path: Path, hierarchy_file: Path, useful_tags_file: Path
) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    (input_dir / "doc.filtered.md").write_text("sidecar")

    runner = CliRunner()
    with (
        patch("ollama.Client.chat") as mock_chat,
        patch("archivatorium.services.tagging_service.TaggingService.extract_tags"),
    ):
        result = runner.invoke(
            cli,
            [
                "metadata",
                str(input_dir),
                str(output_dir),
                "--hierarchy-file",
                str(hierarchy_file),
                "--tags-file",
                str(useful_tags_file),
            ],
        )

    assert result.exit_code == 0
    assert mock_chat.call_count == 0
    assert (output_dir / "doc.filtered.md").read_text() == "sidecar"


def test_metadata_dry_run_is_non_mutating(
    tmp_path: Path, hierarchy_file: Path, useful_tags_file: Path
) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    existing = output_dir / "existing.md"
    existing.write_text("existing")
    (input_dir / "doc.md").write_text("body")
    (input_dir / "source.pdf").write_bytes(b"pdf")
    (input_dir / "notes.txt").write_text("notes")

    before = {
        path.relative_to(output_dir).as_posix(): path.read_bytes()
        for path in output_dir.rglob("*")
        if path.is_file()
    }
    runner = CliRunner()
    with (
        patch("ollama.Client.chat") as mock_chat,
        patch("archivatorium.services.tagging_service.TaggingService.extract_tags") as mock_tags,
    ):
        result = runner.invoke(
            cli,
            [
                "metadata",
                str(input_dir),
                str(output_dir),
                "--dry-run",
                "--hierarchy-file",
                str(hierarchy_file),
                "--tags-file",
                str(useful_tags_file),
            ],
        )

    after = {
        path.relative_to(output_dir).as_posix(): path.read_bytes()
        for path in output_dir.rglob("*")
        if path.is_file()
    }
    assert result.exit_code == 0
    assert before == after
    assert not (output_dir / "doc.md").exists()
    assert not (output_dir / "pdf" / "source.pdf").exists()
    assert mock_chat.call_count == 0
    assert mock_tags.call_count == 0
