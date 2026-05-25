from ocrpolish.services.interlinking_service import InterlinkingService


def test_interlink_unification(tmp_path):
    # Setup a mock vault
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    
    # Doc 1: Canonical code
    doc1 = vault_dir / "doc1.md"
    doc1.write_text("""---
archive_code: NPG(SG)N(72)65
language: English
---
# Doc 1
""", encoding="utf-8")
    
    # Doc 2: Variant code in frontmatter references
    doc2 = vault_dir / "doc2.md"
    doc2.write_text("""---
archive_code: TEST/001
language: English
---
> [!info] Metadata
> | ☰&nbsp;references: | NPG(Staff Group)N(72)65 |
> | ≡&nbsp;language: | English |

# Doc 2
Referencing NPG(StaffGroup)N(72)65 in body.
""", encoding="utf-8")
    
    service = InterlinkingService(vault_dir)
    service.discover()
    service.interlink_all()
    
    # Verify doc2 was updated
    content2 = doc2.read_text(encoding="utf-8")
    assert "[NPG(SG)N(72)65](doc1.md)" in content2 or "[NPG(Staff Group)N(72)65](doc1.md)" in content2
    assert "[NPG(StaffGroup)N(72)65](doc1.md)" in content2
