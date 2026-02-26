from pathlib import Path

from ocrpolish.core import run_processing
from ocrpolish.data_model import ProcessingConfig


def test_sidecar_output_integration(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    bp = "BOILERPLATE LINE"
    (input_dir / "doc1.md").write_text(f"{bp}\n\nContent 1")
    (input_dir / "doc2.md").write_text(f"{bp}\n\nContent 2")

    # Create filter file
    filter_file = tmp_path / "filters.txt"
    filter_file.write_text(f"{bp}\n")

    config = ProcessingConfig(
        input_dir=input_dir, output_dir=output_dir, save_filtered=True, filter_file_path=filter_file
    )

    run_processing(config)

    filtered1 = output_dir / "doc1.md.filtered.md"
    assert filtered1.exists()
    assert bp in filtered1.read_text()


def test_sidecar_unaffected_by_docx_metadata(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    docx_dir = tmp_path / "docx"
    input_dir.mkdir()

    filtered_term = "CONFIDENTIAL"
    content = f"# Page 1\n-1-\n{filtered_term}\nActual body content"
    (input_dir / "test.md").write_text(content)

    filter_file = tmp_path / "filters.txt"
    filter_file.write_text(f"{filtered_term}\n")

    config = ProcessingConfig(
        input_dir=input_dir,
        output_dir=output_dir,
        docx_output_dir=docx_dir,
        save_filtered=True,
        filter_file_path=filter_file,
    )

    run_processing(config)

    # DOCX should have moved it
    docx_file = docx_dir / "test.docx"
    assert docx_file.exists()

    # Filtered MD should still have it
    filtered_md = output_dir / "test.md.filtered.md"
    assert filtered_md.exists()
    assert filtered_term in filtered_md.read_text()
