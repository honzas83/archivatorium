import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from ocrpolish.cli import main


def test_reworked_logic_integration(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    # Create sample files
    # "NATO SECRET" will appear 7 times total across 3 files
    file1_content = "NATO SECRET\nLine 1\nNATO SECRET\nLine 2\nNATO SECRET\n"
    file2_content = "NATO SECRET\nLine 3\nNATO SECRET\nLine 4\nNATO SECRET\n"
    # "NATO Secret" with punctuation should be normalized to the same pattern (CASE MATTERS NOW)
    file3_content = "NATO SECRET\nLine 5\n"

    (input_dir / "doc1.md").write_text(file1_content)
    (input_dir / "doc2.md").write_text(file2_content)
    (input_dir / "doc3.md").write_text(file3_content)

    # Run with frequency file generation
    freq_file = "my_freq.txt"
    argv = ["ocrpolish", str(input_dir), str(output_dir), "--frequency-file", freq_file]
    with patch.object(sys, "argv", argv):
        main()

    # Check frequency report
    report_path = output_dir / freq_file
    assert report_path.exists()
    report_content = report_path.read_text()

    # "NATO SECRET" appeared 7 times across 3 files
    assert "7 (3): NATO SECRET" in report_content

    # Now test filtering and frequency interaction
    filter_file = tmp_path / "filters.txt"
    # Filter "NATO SECRET"
    filter_file.write_text("NATO SECRET\n")

    output_dir_2 = tmp_path / "output_filtered"
    freq_file_filtered = "freq_after_filter.txt"
    argv_filtered = [
        "ocrpolish",
        str(input_dir),
        str(output_dir_2),
        "--filter-file",
        str(filter_file),
        "--frequency-file",
        freq_file_filtered,
    ]
    with patch.object(sys, "argv", argv_filtered):
        main()

    # The frequency report should NOT contain "NATO SECRET" now because it was filtered out
    report_filtered_content = (output_dir_2 / freq_file_filtered).read_text()
    assert "NATO SECRET" not in report_filtered_content

    # Verify structural markers are ignored in frequency report
    # We add # Page 10 and - 5 - several times
    input_dir_structural = tmp_path / "input_structural"
    input_dir_structural.mkdir()
    (input_dir_structural / "doc.md").write_text("# Page 10\n# Page 10\n- 5 -\n- 5 -\nContent\n")

    output_dir_structural = tmp_path / "output_structural"
    with patch.object(
        sys, "argv", ["ocrpolish", str(input_dir_structural), str(output_dir_structural)]
    ):
        main()

    report_structural = (output_dir_structural / "frequency.txt").read_text()
    assert "# Page 10" not in report_structural
    assert "- 5 -" not in report_structural

    doc1_out = (output_dir_2 / "doc1.md").read_text()
    assert "NATO SECRET" not in doc1_out

    # Test paragraph protection: "NATO SECRET" should NOT filter a long paragraph containing it
    long_para_content = "This is a long paragraph that mentions NATO SECRET but should not be deleted because it has many words."
    (input_dir / "para.md").write_text(long_para_content)

    output_dir_4 = tmp_path / "output_para_protection"
    with patch.object(
        sys,
        "argv",
        ["ocrpolish", str(input_dir), str(output_dir_4), "--filter-file", str(filter_file)],
    ):
        main()

    para_out = (output_dir_4 / "para.md").read_text()
    # Use normalized comparison to ignore wrapping
    assert long_para_content.replace("\n", " ") in para_out.replace("\n", " ")

    # Test threshold match: "NATO SECRET" (2 words) should filter "NATO SECRET PAGE" (3 words)
    # because 2/3 >= 0.5
    (input_dir / "short.md").write_text("NATO SECRET PAGE")
    output_dir_5 = tmp_path / "output_short_match"
    with patch.object(
        sys,
        "argv",
        ["ocrpolish", str(input_dir), str(output_dir_5), "--filter-file", str(filter_file)],
    ):
        main()
    short_out = (output_dir_5 / "short.md").read_text()
    assert "NATO SECRET PAGE" not in short_out

    # Sidecar filtered file should exist
    filtered_sidecar = output_dir_2 / "doc1.md.filtered.md"
    assert filtered_sidecar.exists()
    assert "NATO SECRET" in filtered_sidecar.read_text()


def test_consecutive_short_lines(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    content = "Line 1\nLine 2\nLine 3\n"
    (input_dir / "short.md").write_text(content)

    with patch.object(sys, "argv", ["ocrpolish", str(input_dir), str(output_dir)]):
        main()

    out_content = (output_dir / "short.md").read_text()
    # Should be exactly same as input (no blank lines added)
    assert out_content == content


def test_wrapping_with_blank_lines(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    # Long paragraph and long list item
    long_text = (
        "This is a very long text that should be wrapped because "
        "it exceeds the default typewriter width of eighty characters."
    )
    content = f"{long_text}\n\n- {long_text}\n- Short item\n"

    (input_dir / "wrapped.md").write_text(content)

    # Set width to 40 to ensure wrapping
    with patch.object(sys, "argv", ["ocrpolish", str(input_dir), str(output_dir), "--width", "40"]):
        main()

    out_content = (output_dir / "wrapped.md").read_text()

    # Paragraph was wrapped -> should have blank line after it
    # List item was wrapped -> should have blank line after it
    # Short item was NOT wrapped -> should NOT have blank line after it

    # Check for blank lines. After wrapping 'long_text' (width 40), it will be 3 lines.
    # We expect:
    # Line 1
    # Line 2
    # Line 3
    # (blank line)
    # - Line 1
    # Line 2
    # Line 3
    # (blank line)
    # - Short item

    lines = out_content.splitlines()

    # Find "- Short item"
    try:
        short_item_idx = lines.index("- Short item")
    except ValueError:
        pytest.fail("'- Short item' not found in output")

    def test_table_formatting(tmp_path: Path) -> None:
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        input_dir.mkdir()

        table_content = (
            "| Header 1 | Long Header 2 |\n"
            "|---|---|\n"
            "| short | very long cell content |\n"
            "| 1 | 2 |\n"
        )
        (input_dir / "table.md").write_text(table_content)

        with patch.object(sys, "argv", ["ocrpolish", str(input_dir), str(output_dir)]):
            main()

        out_content = (output_dir / "table.md").read_text()
        lines = out_content.splitlines()

        # Check alignment
        # Long Header 2 is length 13. "very long cell content" is 22.
        # Col 1 max is "Header 1" (8).
        # Expected Col 1 width: 8. Expected Col 2 width: 22.
        assert "| Header 1 | Long Header 2          |" in lines[0]
        assert "|----------|------------------------|" in lines[1]
        assert "| short    | very long cell content |" in lines[2]
        assert "| 1        | 2                      |" in lines[3]
