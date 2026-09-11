from __future__ import annotations

from pathlib import Path
from threading import Barrier, Lock
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from archivatorium.cli import cli


def test_ocr_processes_independent_pdfs_in_parallel(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    for name in ("one.pdf", "two.pdf"):
        (input_dir / name).write_bytes(b"synthetic")

    barrier = Barrier(2)
    state_lock = Lock()
    state = {"active": 0, "maximum": 0}

    class FakeEngine:
        def __init__(self, **_kwargs: object) -> None:
            self.last_run_attempted_pages = 0

        def run_ocr(self, input_pdf: Path, output_md: Path, page_header: bool) -> str:
            assert page_header is True
            with state_lock:
                state["active"] += 1
                state["maximum"] = max(state["maximum"], state["active"])
            barrier.wait(timeout=2)
            output_md.parent.mkdir(parents=True, exist_ok=True)
            text = input_pdf.stem.upper()
            output_md.write_text(text, encoding="utf-8")
            self.last_run_attempted_pages = 1
            with state_lock:
                state["active"] -= 1
            return text

    with patch("archivatorium.ocr_engine.OCREngine", FakeEngine):
        result = CliRunner().invoke(
            cli,
            ["ocr", str(input_dir), str(output_dir), "--concurrency", "2"],
        )

    assert result.exit_code == 0, result.output
    assert state["maximum"] == 2
    assert (output_dir / "one.md").read_text(encoding="utf-8") == "ONE"
    assert (output_dir / "two.md").read_text(encoding="utf-8") == "TWO"
    assert "overall_attempted_pages=2" in result.output


@pytest.mark.parametrize("value", ["0", "5"])
def test_ocr_rejects_concurrency_outside_account_limit(tmp_path: Path, value: str) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    result = CliRunner().invoke(
        cli,
        ["ocr", str(input_dir), str(tmp_path / "output"), "--concurrency", value],
    )

    assert result.exit_code == 2
    assert "1<=x<=4" in result.output


def test_ocr_help_documents_concurrency_option() -> None:
    result = CliRunner().invoke(cli, ["ocr", "--help"])

    assert result.exit_code == 0
    assert "--concurrency" in result.output


def test_parallel_pdf_failure_does_not_cancel_other_outputs(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    for name in ("bad.pdf", "good.pdf"):
        (input_dir / name).write_bytes(b"synthetic")

    class FakeEngine:
        def __init__(self, **_kwargs: object) -> None:
            self.last_run_attempted_pages = 0

        def run_ocr(self, input_pdf: Path, output_md: Path, page_header: bool) -> str:
            assert page_header is True
            self.last_run_attempted_pages = 1
            if input_pdf.stem == "bad":
                raise RuntimeError("synthetic failure")
            output_md.parent.mkdir(parents=True, exist_ok=True)
            output_md.write_text("GOOD", encoding="utf-8")
            return "GOOD"

    with patch("archivatorium.ocr_engine.OCREngine", FakeEngine):
        result = CliRunner().invoke(
            cli,
            ["ocr", str(input_dir), str(output_dir), "--concurrency", "2"],
        )

    assert result.exit_code == 0, result.output
    assert "Error processing bad.pdf: synthetic failure" in result.output
    assert not (output_dir / "bad.md").exists()
    assert (output_dir / "good.md").read_text(encoding="utf-8") == "GOOD"
    assert "overall_attempted_pages=2" in result.output
