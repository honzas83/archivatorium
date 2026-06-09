from pathlib import Path

from ocrpolish.processor_metadata import MetadataProcessor


class MockOllamaClient:
    def extract_structured(self, prompt, schema, model=None, think=False):
        # Return empty schema objects for mocking
        return schema()


def test_preflight_scan_and_overwrite(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Create an existing output file in output directory
    existing_file = output_dir / "doc1.md"
    existing_file.write_text(
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
        overwrite=True,
    )

    # 1. Trigger preflight scan manually to initialize
    processor.preflight_scan()

    # Verify initial scanned counts
    assert processor.entity_counts["State"]["belgium"] == 1
    assert processor.entity_counts["Org"]["nato"] == 1
    assert processor.conceptual_tag_counts["conceptual-tag"] == 1

    # Verify the registry recorded doc1.md's tags
    assert existing_file in processor.scanned_files_tags
    old_tags = processor.scanned_files_tags[existing_file]
    assert "Entities/State/Belgium" in old_tags.raw_paths

    # 2. Overwrite the file with new contents (e.g. NATO is removed, France added)
    new_content = """---
title: Updated Document
---
> [!abstract]
> ## Entities
> * States
>   - #Entities/State/Belgium
>   - #Entities/State/France
> 
> ## Tags
> #Tags/Conceptual-Tag
"""
    # Simulate processing doc1.md (subtract doc1.md old tags, add new tags)
    processor._update_file_counters(existing_file, new_content)

    # Verify updated counts (NATO should be 0, France should be 1, Belgium remains 1)
    assert processor.entity_counts["State"]["belgium"] == 1
    assert processor.entity_counts["State"]["france"] == 1
    assert processor.entity_counts["Org"]["nato"] == 0
    assert processor.conceptual_tag_counts["conceptual-tag"] == 1
