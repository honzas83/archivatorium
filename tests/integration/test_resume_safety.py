from pathlib import Path

from ocrpolish.processor_metadata import MetadataProcessor


class MockOllamaClient:
    def extract_structured(self, prompt, schema, model=None, think=False):
        return schema()


def test_resume_safety_preflight_and_counters(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    # Create an input file
    input_file = input_dir / "doc1.md"
    input_file.write_text("Clean body text", encoding="utf-8")

    # Create an already processed file in output directory
    output_file = output_dir / "doc1.md"
    output_file.write_text(
        """---
title: Existing Document
---
> [!abstract]
> ## Entities
> * States
>   - #Entities/State/Belgium
> * Organisations
>   - #Entities/Org/NATO
> 
> ## Tags
> #Tags/Conceptual-Tag
""",
        encoding="utf-8",
    )

    ollama = MockOllamaClient()
    processor = MetadataProcessor(
        ollama_client=ollama,  # type: ignore
        output_dir=output_dir,
        overwrite=False,
    )

    # 1. Trigger preflight scan manually
    processor.preflight_scan()

    # Verify counts from preflight scan
    assert processor.entity_counts["State"]["belgium"] == 1
    assert processor.entity_counts["Org"]["nato"] == 1
    assert processor.conceptual_tag_counts["conceptual-tag"] == 1

    # Verify cache is populated
    assert output_file in processor.scanned_files_tags

    # 2. Try calling preflight scan again; it should return early and not modify counts
    processor.preflight_scan()
    assert processor.entity_counts["State"]["belgium"] == 1

    # 3. Process the file (it exists and overwrite=False)
    # It should skip, and since it was already in scanned_files_tags, it should not double count.
    result = processor.process_file(input_file, output_file)
    assert result is False  # skipped

    # Counts must remain exactly 1 (not double counted to 2)
    assert processor.entity_counts["State"]["belgium"] == 1
    assert processor.entity_counts["Org"]["nato"] == 1
    assert processor.conceptual_tag_counts["conceptual-tag"] == 1


def test_resume_safety_skipped_but_not_in_preflight(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    # Create an input file
    input_file = input_dir / "doc2.md"
    input_file.write_text("Clean body text", encoding="utf-8")

    # Create output file
    output_file = output_dir / "doc2.md"
    output_file.write_text(
        """---
title: Doc 2
---
> [!abstract]
> ## Entities
> * States
>   - #Entities/State/Germany
""",
        encoding="utf-8",
    )

    ollama = MockOllamaClient()
    processor = MetadataProcessor(
        ollama_client=ollama,  # type: ignore
        output_dir=output_dir,
        overwrite=False,
    )

    # We do NOT run preflight scan manually, or run it but clear the scanned cache
    # to simulate a file that exists but wasn't scanned.
    processor.preflight_scan()
    processor.scanned_files_tags.clear()
    processor.entity_counts["State"].clear()

    # Process file; since overwrite=False and output exists, it skips.
    # But since it's not in scanned_files_tags, it should parse and add its tags.
    result = processor.process_file(input_file, output_file)
    assert result is False  # skipped

    # The skipped file's tags must be parsed and added to counters
    assert processor.entity_counts["State"]["germany"] == 1
    assert output_file in processor.scanned_files_tags
