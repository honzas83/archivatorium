from collections import Counter
from pathlib import Path
from unittest.mock import MagicMock

from archivatorium.models.metadata import CanonicalTags
from archivatorium.processor_metadata import MetadataProcessor


def test_parallel_metadata_worker_owns_an_isolated_preflight_snapshot(tmp_path: Path) -> None:
    client = MagicMock()
    tagging_service = MagicMock()
    processor = MetadataProcessor(
        ollama_client=client,
        output_dir=tmp_path / "output",
        tagging_service=tagging_service,
    )
    source = tmp_path / "existing.md"
    processor.conceptual_tag_counts = Counter({"Existing": 3})
    processor.established_conceptual_tags = {"Existing"}
    processor.topic_counts = Counter({"Category/Topic": 2})
    processor.entity_counts["Org"]["NATO"] = 4
    processor.scanned_files_tags[source] = CanonicalTags(conceptual_tags={"Existing"})
    processor._preflight_done = True

    worker = processor.fork_for_parallel_document()

    assert worker is not processor
    assert worker.client is client
    assert worker.tagging_service is tagging_service
    assert worker.conceptual_tag_counts == processor.conceptual_tag_counts
    assert worker.entity_counts == processor.entity_counts
    assert worker.scanned_files_tags == processor.scanned_files_tags
    assert worker._preflight_done is True

    worker.conceptual_tag_counts["Existing"] += 1
    worker.entity_counts["Org"]["NATO"] += 1
    worker.scanned_files_tags.clear()

    assert processor.conceptual_tag_counts["Existing"] == 3
    assert processor.entity_counts["Org"]["NATO"] == 4
    assert source in processor.scanned_files_tags


def test_successful_parallel_output_updates_global_counters(tmp_path: Path) -> None:
    output_file = tmp_path / "output" / "document.md"
    output_file.parent.mkdir()
    output_file.write_text(
        """> [!abstract]
> ## Entities
> * Organisations
>   - #Entities/Org/NATO
>
> ## Tags
> #Tags/Parallel-Tag
""",
        encoding="utf-8",
    )
    processor = MetadataProcessor(
        ollama_client=MagicMock(),
        output_dir=output_file.parent,
    )

    processor.ingest_parallel_output(output_file)

    assert processor.entity_counts["Org"]["nato"] == 1
    assert processor.conceptual_tag_counts["parallel-tag"] == 1
    assert output_file in processor.scanned_files_tags
