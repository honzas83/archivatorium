from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from ocrpolish.cli import cli


def test_vault_initialization_via_cli():
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Setup input directory
        input_dir = Path("input")
        input_dir.mkdir()
        (input_dir / "test.md").write_text("This is a test document.")

        # Setup template directory (must be in CWD for cli.py to find it)
        template_dir = Path("obsidian_template")
        template_dir.mkdir()
        (template_dir / ".obsidian").mkdir()
        (template_dir / ".obsidian" / "app.json").write_text('{"propertiesInDocument": "hidden"}')
        (template_dir / ".obsidian" / "appearance.json").write_text('{"accentColor": "purple"}')
        (template_dir / "CONTENT.base").write_text("Base content template")

        output_dir = Path("output")

        # Mock the MetadataProcessor to avoid actual Ollama/processing overhead
        with patch("ocrpolish.processor_metadata.MetadataProcessor.process_file"):
            # We don't care about what process_file does, just that it's called (or not)
            result = runner.invoke(cli, ["metadata", str(input_dir), str(output_dir)])

            assert result.exit_code == 0

            # Verify that the vault configuration was initialized
            assert (output_dir / ".obsidian" / "app.json").exists()
            assert (output_dir / ".obsidian" / "appearance.json").exists()
            assert (output_dir / "CONTENT.base").exists()

            # Verify content integrity
            app_json_content = (output_dir / ".obsidian" / "app.json").read_text()
            assert app_json_content == '{"propertiesInDocument": "hidden"}'
            assert (output_dir / "CONTENT.base").read_text() == "Base content template"


def test_vault_initialization_skipped_in_dry_run():
    runner = CliRunner()

    with runner.isolated_filesystem():
        input_dir = Path("input")
        input_dir.mkdir()
        (input_dir / "test.md").write_text("test")

        template_dir = Path("obsidian_template")
        template_dir.mkdir()
        (template_dir / "CONTENT.base").write_text("base")

        output_dir = Path("output")

        with patch("ocrpolish.processor_metadata.MetadataProcessor.process_file"):
            result = runner.invoke(cli, ["metadata", str(input_dir), str(output_dir), "--dry-run"])

            assert result.exit_code == 0
            # Should NOT be initialized in dry-run
            assert not (output_dir / "CONTENT.base").exists()
