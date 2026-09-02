from pathlib import Path

from click.testing import CliRunner, Result

from archivatorium.cli import cli
from archivatorium.services.flattening_service import TaxonomyValidationError

ROOT = Path(__file__).parents[2]
V1 = ROOT / "topics" / "NATO_themes.yaml"
V2 = ROOT / "topics" / "NATO_themes_v2.yaml"
TAGS = ROOT / "topics" / "USEFUL_TAGS.yaml"


def _invoke_dry_run(input_dir: Path, output_dir: Path, hierarchy: Path) -> Result:
    return CliRunner().invoke(
        cli,
        [
            "metadata",
            str(input_dir),
            str(output_dir),
            "--hierarchy-file",
            str(hierarchy),
            "--tags-file",
            str(TAGS),
            "--dry-run",
        ],
    )


def test_cli_explicitly_selects_v1_or_v2_without_rewriting_prior_output(
    tmp_path: Path,
) -> None:
    input_dir = tmp_path / "input"
    nested = input_dir / "series" / "1978"
    nested.mkdir(parents=True)
    (nested / "document.md").write_text("Substantive NATO policy.", encoding="utf-8")
    old_output = tmp_path / "output-v1"
    old_output.mkdir()
    sentinel = old_output / "existing.md"
    sentinel.write_text("unchanged-v1-output", encoding="utf-8")

    v1_result = _invoke_dry_run(input_dir, old_output, V1)
    v2_result = _invoke_dry_run(input_dir, tmp_path / "output-v2", V2)

    assert v1_result.exit_code == 0, v1_result.output
    assert v2_result.exit_code == 0, v2_result.output
    assert "series/1978/document.md" in v1_result.output
    assert "series/1978/document.md" in v2_result.output
    assert sentinel.read_text(encoding="utf-8") == "unchanged-v1-output"


def test_cli_rejects_invalid_selected_hierarchy_before_processing(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "document.md").write_text("NATO policy.", encoding="utf-8")
    invalid = tmp_path / "invalid.yaml"
    invalid.write_text("categories: []\n", encoding="utf-8")

    result = _invoke_dry_run(input_dir, tmp_path / "output", invalid)

    assert result.exit_code != 0
    assert isinstance(result.exception, TaxonomyValidationError)
    assert "categories must be a non-empty list" in str(result.exception)
