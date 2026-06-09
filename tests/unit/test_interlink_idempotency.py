from pathlib import Path

from ocrpolish.services.interlinking_service import InterlinkingService


def test_idempotent_interlinking(tmp_path: Path) -> None:
    # Set up a mock vault
    vault = tmp_path / "vault"
    vault.mkdir()

    # Create doc1
    doc1_path = vault / "doc1.md"
    doc1_path.write_text(
        """---
title: Doc 1
archive_code: NPG/D(74)2
language: English
references: []
---
> [!info] Metadata
> | ≡&nbsp;archive_code: | NPG/D(74)2 |
> | ≡&nbsp;language: | English |

This is Doc 1. Mentions NPG/D(75)1.
""",
        encoding="utf-8",
    )

    # Create doc2
    doc2_path = vault / "doc2.md"
    doc2_path.write_text(
        """---
title: Doc 2
archive_code: NPG/D(75)1
language: English
references: []
---
> [!info] Metadata
> | ≡&nbsp;archive_code: | NPG/D(75)1 |
> | ≡&nbsp;language: | English |

This is Doc 2. Mentions NPG/D(74)2.
""",
        encoding="utf-8",
    )

    service = InterlinkingService(vault)
    service.discover()

    # Verify scan results
    assert len(service.documents) == 2
    doc1_record = next(d for d in service.documents if d.path == doc1_path)
    assert doc1_record.archive_code == "NPG/D(74)2"
    assert doc1_record.language == "English"

    # Run interlinking
    service.interlink_all()

    # Verify doc1 mentions doc2 correctly using relative path
    doc1_new_content = doc1_path.read_text(encoding="utf-8")
    assert "[NPG/D(75)1](doc2.md)" in doc1_new_content

    # Run interlinking again (idempotency check)
    service.interlink_all()
    doc1_final_content = doc1_path.read_text(encoding="utf-8")
    assert doc1_new_content == doc1_final_content
    # Make sure we don't have nested links
    assert "[[ [NPG/D(75)1](doc2.md) ]]" not in doc1_final_content
    assert "[[doc2.md]]" not in doc1_final_content


def test_self_linking_prevention(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()

    doc_path = vault / "self_link.md"
    doc_path.write_text(
        """---
title: Self Link Doc
archive_code: NPG/D(74)2
language: English
references: []
---
> [!info] Metadata
> | ≡&nbsp;archive_code: | NPG/D(74)2 |
> | ≡&nbsp;language: | English |

I mention NPG/D(74)2 in my body.
""",
        encoding="utf-8",
    )

    service = InterlinkingService(vault)
    service.discover()
    service.interlink_all()

    content = doc_path.read_text(encoding="utf-8")
    # Should NOT be linked since it's a self-link
    assert "[NPG/D(74)2]" not in content
    assert "self_link.md" not in content
