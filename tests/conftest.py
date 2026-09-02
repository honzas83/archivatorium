from collections.abc import Callable
from pathlib import Path
from typing import Any, cast
from unittest.mock import MagicMock

import pytest

from archivatorium.models.metadata import AggregatedTaggingResult, MetadataSchema, TopicResult
from tests.unit.test_ollama_client import create_mock_ollama_response


@pytest.fixture
def ocr_response_factory() -> Callable[[str], MagicMock]:
    """Build an Ollama-style chat response with deterministic OCR content."""

    def factory(content: str) -> MagicMock:
        response = MagicMock()
        response.message = {"content": content}
        return response

    return factory


@pytest.fixture
def ocr_call_kwargs() -> Callable[[MagicMock, int], dict[str, Any]]:
    """Return captured keyword arguments for a mocked Ollama chat call."""

    def get_call(client: MagicMock, index: int = -1) -> dict[str, Any]:
        return cast(dict[str, Any], client.chat.call_args_list[index].kwargs)

    return get_call


@pytest.fixture
def temp_ocr_dirs(tmp_path: Path) -> tuple[Path, Path]:
    """Create disposable input/output directories with one placeholder PDF."""

    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    (input_dir / "test.pdf").write_bytes(b"dummy pdf content")
    return input_dir, output_dir


@pytest.fixture
def hierarchy_file(tmp_path: Path) -> Path:
    path = tmp_path / "hierarchy.yaml"
    path.write_text(
        """
categories:
  - category: Defence Policy
    description: Defence policy matters
    topics:
      - topic: Nuclear Planning
        description: Nuclear planning documents
        positive_samples: nuclear planning group
        negative_samples: routine agenda
""".lstrip(),
        encoding="utf-8",
    )
    return path


@pytest.fixture
def legacy_hierarchy_file(hierarchy_file: Path) -> Path:
    """Alias the shared minimal hierarchy as an explicit legacy taxonomy fixture."""
    return hierarchy_file


@pytest.fixture
def v2_hierarchy_file(tmp_path: Path) -> Path:
    """Create a minimal schema-v2 hierarchy for service-level tests."""
    path = tmp_path / "hierarchy_v2.yaml"
    path.write_text(
        """
schema_version: 2
classification_policy:
  substantive_subject_rule: Assign only important subjects treated substantively.
  omission_rule: Prefer omission; an empty thematic-topic list is valid.
  insufficient_evidence_rule: A mention, entity, title, citation, or meeting is insufficient alone.
categories:
  - category: Nuclear Doctrine and Deterrence
    description: Nuclear doctrines that deter aggression.
    topics:
      - topic: Nuclear Deterrence
        description: Substantive analysis of deterrence through nuclear retaliation.
        positive_samples: |
          Credibility of the nuclear deterrent
        negative_samples: |
          A passing mention of nuclear weapons
""".lstrip(),
        encoding="utf-8",
    )
    return path


@pytest.fixture
def useful_tags_file(tmp_path: Path) -> Path:
    path = tmp_path / "useful_tags.yaml"
    path.write_text(
        """
useful_tags:
  - Nuclear Planning
  - NATO
  - Ministerial Guidance
""".lstrip(),
        encoding="utf-8",
    )
    return path


@pytest.fixture
def metadata_response_factory() -> Callable[..., Any]:
    def factory(**overrides: Any) -> Any:
        data = {
            "title": "Test Document",
            "summary": "This is a test document.",
            "abstract": "This is a detailed test abstract.",
            "language": "English",
            "date": "1981-11-19",
            "archive_code": "TEST-1",
        }
        data.update(overrides)
        return create_mock_ollama_response(MetadataSchema(**data).model_dump_json())

    return factory


@pytest.fixture
def tagging_result() -> AggregatedTaggingResult:
    return AggregatedTaggingResult(
        conceptual_tags=["NATO"],
        entity_tags=["Org/NATO"],
        topic_tags=[
            TopicResult(
                topic="Defence Policy/Nuclear Planning",
                reason='The text mentions "nuclear planning group".',
            )
        ],
    )


@pytest.fixture
def mixed_vault_factory(tmp_path: Path) -> Callable[[], Path]:
    def factory() -> Path:
        vault = tmp_path / "vault"
        vault.mkdir()
        (vault / "doc.md").write_text("# Document\n#Tags/Document-Only\n", encoding="utf-8")
        (vault / "Index - Tags.md").write_text("#Tags/Index-Only\n", encoding="utf-8")
        (vault / "index.md").write_text("#Tags/Landing-Only\n", encoding="utf-8")
        (vault / "doc.filtered.md").write_text("#Tags/Sidecar-Only\n", encoding="utf-8")
        templates = vault / "templates"
        templates.mkdir()
        (templates / "template.md").write_text("#Tags/Template-Only\n", encoding="utf-8")
        hidden = vault / ".obsidian"
        hidden.mkdir()
        (hidden / "support.md").write_text("#Tags/Hidden-Only\n", encoding="utf-8")
        return vault

    return factory


@pytest.fixture
def substantive_text() -> str:
    return (
        "The NATO Nuclear Planning Group discussed nuclear release procedures, "
        "consultation procedures, deterrence strategy, WINTEX 71 exercises, "
        "SACEUR command arrangements, and operational doctrine."
    )


@pytest.fixture
def administrative_stub_text() -> str:
    return "This document is incorporated into the initial document and cancelled."


@pytest.fixture
def assert_filesystem_unchanged() -> Callable[[Path, dict[str, tuple[bool, bytes]]], None]:
    def snapshot(root: Path) -> dict[str, tuple[bool, bytes]]:
        paths = {root}
        if root.exists():
            paths.update(root.rglob("*"))
        return {
            str(path.relative_to(root) if path != root else Path(".")): (
                path.is_file(),
                path.read_bytes() if path.is_file() else b"",
            )
            for path in sorted(paths)
        }

    def assert_unchanged(root: Path, before: dict[str, tuple[bool, bytes]]) -> None:
        assert snapshot(root) == before

    assert_unchanged.snapshot = snapshot  # type: ignore[attr-defined]
    return assert_unchanged
