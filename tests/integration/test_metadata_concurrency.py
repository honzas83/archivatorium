from __future__ import annotations

from collections import Counter
from pathlib import Path
from threading import Barrier, Lock
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from archivatorium.cli import cli


def _metadata_args(tmp_path: Path) -> list[str]:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    for name in ("one.md", "two.md"):
        (input_dir / name).write_text("synthetic", encoding="utf-8")
    hierarchy = tmp_path / "hierarchy.yaml"
    hierarchy.write_text("categories: []\n", encoding="utf-8")
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


def test_metadata_processes_independent_documents_in_parallel(tmp_path: Path) -> None:
    barrier = Barrier(2)
    state_lock = Lock()
    state = {"active": 0, "maximum": 0}
    ingested: set[Path] = set()

    class FakeProcessor:
        def __init__(self, **_kwargs: object) -> None:
            self.conceptual_tag_counts: Counter[str] = Counter()

        def preflight_scan(self) -> None:
            pass

        def get_files(self, input_dir: Path, mask: str, all_files: bool) -> list[Path]:
            del mask, all_files
            return list(input_dir.glob("*.md"))

        def fork_for_parallel_document(self) -> FakeProcessor:
            return FakeProcessor()

        def ingest_parallel_output(self, output_file: Path) -> None:
            ingested.add(output_file)

        def process_file(
            self, input_file: Path, output_file: Path, _frequent_tags: list[str]
        ) -> bool:
            with state_lock:
                state["active"] += 1
                state["maximum"] = max(state["maximum"], state["active"])
            barrier.wait(timeout=2)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(input_file.stem.upper(), encoding="utf-8")
            with state_lock:
                state["active"] -= 1
            return True

    with (
        patch("archivatorium.cli.build_llm_client", return_value=MagicMock()),
        patch("archivatorium.cli.TaggingService"),
        patch("archivatorium.cli.MetadataProcessor", FakeProcessor),
    ):
        result = CliRunner().invoke(cli, _metadata_args(tmp_path) + ["--concurrency", "2"])

    assert result.exit_code == 0, result.output
    assert state["maximum"] == 2
    assert (tmp_path / "output" / "one.md").read_text(encoding="utf-8") == "ONE"
    assert (tmp_path / "output" / "two.md").read_text(encoding="utf-8") == "TWO"
    assert ingested == {tmp_path / "output" / "one.md", tmp_path / "output" / "two.md"}


@pytest.mark.parametrize("value", ["0", "5"])
def test_metadata_rejects_concurrency_outside_account_limit(tmp_path: Path, value: str) -> None:
    result = CliRunner().invoke(cli, _metadata_args(tmp_path) + ["--concurrency", value])

    assert result.exit_code == 2
    assert "1<=x<=4" in result.output


def test_metadata_help_documents_concurrency_option() -> None:
    result = CliRunner().invoke(cli, ["metadata", "--help"])

    assert result.exit_code == 0
    assert "--concurrency" in result.output


def test_metadata_default_does_not_fork_processor(tmp_path: Path) -> None:
    class FakeProcessor:
        def __init__(self, **_kwargs: object) -> None:
            self.conceptual_tag_counts: Counter[str] = Counter()

        def preflight_scan(self) -> None:
            pass

        def get_files(self, input_dir: Path, mask: str, all_files: bool) -> list[Path]:
            del mask, all_files
            return list(input_dir.glob("*.md"))

        def fork_for_parallel_document(self) -> FakeProcessor:
            raise AssertionError("default metadata path must remain sequential")

        def ingest_parallel_output(self, _output_file: Path) -> None:
            raise AssertionError("default metadata path must not reconcile parallel output")

        def process_file(
            self, _input_file: Path, _output_file: Path, _frequent_tags: list[str]
        ) -> bool:
            return True

    with (
        patch("archivatorium.cli.build_llm_client", return_value=MagicMock()),
        patch("archivatorium.cli.TaggingService"),
        patch("archivatorium.cli.MetadataProcessor", FakeProcessor),
    ):
        result = CliRunner().invoke(cli, _metadata_args(tmp_path))

    assert result.exit_code == 0, result.output
