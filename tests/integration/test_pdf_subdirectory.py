from unittest.mock import patch

from click.testing import CliRunner

from archivatorium.cli import cli
from archivatorium.models.metadata import MetadataSchema
from archivatorium.utils.metadata import parse_frontmatter
from tests.unit.test_ollama_client import create_mock_ollama_response


def test_mirroring_pdf_subdirectory(tmp_path, hierarchy_file, useful_tags_file):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    # Create source structure
    subfolder = input_dir / "project-a"
    subfolder.mkdir()

    md_file = subfolder / "notes.md"
    md_file.write_text("Markdown content")

    pdf_file = subfolder / "notes.pdf"
    pdf_file.write_bytes(b"PDF content")

    runner = CliRunner()

    mock_metadata = {"title": "Test Document", "summary": "Summary", "tags": ["test"]}

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

    # Verify PDF location
    expected_pdf = output_dir / "project-a" / "pdf" / "notes.pdf"
    assert expected_pdf.exists()

    # Verify MD link
    expected_md = output_dir / "project-a" / "notes.md"
    assert expected_md.exists()

    content = expected_md.read_text()
    metadata, body = parse_frontmatter(content)

    assert metadata["source"] == "[[pdf/notes.pdf]]"


def test_mirroring_pdf_collision_reports_error(tmp_path, hierarchy_file, useful_tags_file):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    (input_dir / "notes.md").write_text("Markdown content")
    (input_dir / "notes.pdf").write_bytes(b"PDF content")
    existing_pdf_dir = output_dir / "pdf"
    existing_pdf_dir.mkdir()
    (existing_pdf_dir / "notes.pdf").write_bytes(b"different PDF content")

    runner = CliRunner()
    mock_metadata = {"title": "Test Document", "summary": "Summary"}

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

    assert "Ambiguous mirrored PDF target already exists" in result.output


def test_mirroring_pdf_nested_source_layout(tmp_path, hierarchy_file, useful_tags_file):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    nested = input_dir / "NPG - Nuclear Planning Group" / "1 NPG - Nuclear Planning Group" / "1973"
    nested.mkdir(parents=True)
    output_dir.mkdir()

    (nested / "NPG-D(73)11_FRE.md").write_text("Markdown content")
    (nested / "NPG-D(73)11_FRE.pdf").write_bytes(b"PDF content")

    runner = CliRunner()
    mock_metadata = {"title": "Test Document", "summary": "Summary"}

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
    expected_pdf = (
        output_dir
        / "NPG - Nuclear Planning Group"
        / "1 NPG - Nuclear Planning Group"
        / "1973"
        / "pdf"
        / "NPG-D(73)11_FRE.pdf"
    )
    expected_md = (
        output_dir
        / "NPG - Nuclear Planning Group"
        / "1 NPG - Nuclear Planning Group"
        / "1973"
        / "NPG-D(73)11_FRE.md"
    )

    assert expected_pdf.exists()
    metadata, _ = parse_frontmatter(expected_md.read_text())
    assert metadata["source"] == "[[pdf/NPG-D(73)11_FRE.pdf]]"
