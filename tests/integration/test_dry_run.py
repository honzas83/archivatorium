from pathlib import Path

from archivatorium.core import run_processing
from archivatorium.data_model import ProcessingConfig


def test_dry_run_integration(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    (input_dir / "doc.md").write_text("Some content\n")

    config = ProcessingConfig(input_dir=input_dir, output_dir=output_dir, dry_run=True)

    run_processing(config)

    # Primary output should NOT exist
    out_file = output_dir / "doc.md"
    assert not out_file.exists()
