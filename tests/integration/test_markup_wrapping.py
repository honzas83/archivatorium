from pathlib import Path

from ocrpolish.core import run_processing
from ocrpolish.data_model import ProcessingConfig


def test_markup_wrapping_integration(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    # Text with markup at start of line
    content = (
        "<PAGE 1>\n"
        "[SECRET]\n"
        "This is a very long line of text that should definitely be wrapped "
        "because it exceeds the default typewriter width of eighty characters.\n"
        "And another paragraph."
    )
    (input_dir / "doc.md").write_text(content)

    config = ProcessingConfig(input_dir=input_dir, output_dir=output_dir, typewriter_width=40)

    run_processing(config)

    out_file = output_dir / "doc.md"
    assert out_file.exists()

    out_content = out_file.read_text()

    # NEW RULE: short lines are NOT separated by blank lines if they were not wrapped.
    # <PAGE 1> and [SECRET] are short, so they should stay together.
    # The long line IS wrapped, so it SHOULD be followed by a blank line.

    expected_start = "<PAGE 1>\n[SECRET]\n"
    assert out_content.startswith(expected_start)

    # Check for blank line after the wrapped paragraph
    assert "\neighty characters.\n\nAnd another paragraph.\n" in out_content
