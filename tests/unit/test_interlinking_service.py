from pathlib import Path

from ocrpolish.services.interlinking_service import InterlinkingService


def test_service_initialization() -> None:
    vault_dir = Path("/tmp/vault")
    service = InterlinkingService(vault_dir)
    assert service.vault_dir == vault_dir
    assert service.code_map == {}
    assert service.bibtex_map == {}

def test_normalize_code(tmp_path) -> None:
    service = InterlinkingService(tmp_path)
    assert service.normalize_code("DPC / D (69) 58") == "DPC/D(69)58"
    assert service.normalize_code("CODE-123") == "CODE/123"
    assert service.normalize_code("") == ""

def test_resolve_link_priority():
    service = InterlinkingService(Path("/tmp"))
    service.code_map = {
        "CODE1": {
            "English": "path/en.md",
            "French": "path/fr.md",
            "German": "path/de.md"
        }
    }
    service.bibtex_map = {
        "CODE1": {
            "French": "path/fr_fuzzy.md",
            "English": "path/en_fuzzy.md"
        }
    }
    
    # 1. Exact match in source_lang
    assert service.resolve_link("CODE1", "French") == "path/fr.md"
    
    # 2. BibTeX fuzzy match in source_lang
    # (Setup CODE2 with only fuzzy in French, but exact in English)
    service.code_map["CODE2"] = {"English": "path/en2.md"}
    service.bibtex_map["CODE2"] = {"French": "path/fr2_fuzzy.md"}
    assert service.resolve_link("CODE2", "French") == "path/fr2_fuzzy.md"
    
    # 3. Exact match in English
    service.code_map["CODE3"] = {"English": "path/en3.md"}
    service.bibtex_map["CODE3"] = {"German": "path/de3_fuzzy.md"}
    assert service.resolve_link("CODE3", "French") == "path/en3.md"
    
    # 4. BibTeX fuzzy match in English
    service.bibtex_map["CODE4"] = {"English": "path/en4_fuzzy.md"}
    assert service.resolve_link("CODE4", "French") == "path/en4_fuzzy.md"
    
    # 5. Exact match in any
    service.code_map["CODE5"] = {"German": "path/de5.md"}
    assert service.resolve_link("CODE5", "French") == "path/de5.md"
    
    # Missing code
    assert service.resolve_link("MISSING", "English") is None

def test_resolve_link_bibtex_fallback():
    service = InterlinkingService(Path("/tmp"))
    # NPG/D(74)2 becomes NPG-D-74-2 in bibtex_map
    service.bibtex_map = {
        "NPG-D-74-2": {"English": "npg-74-2.md"}
    }
    
    # Should resolve NPG/D(74)/2 using BibTeX key NPG-D-74-2
    assert service.resolve_link("NPG/D(74)/2", "English") == "npg-74-2.md"

def test_discover_filenames_only(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    
    doc = vault / "doc.md"
    doc.write_text("""---
archive_code: NPG/D(74)2
language: English
---
""", encoding="utf-8")
    
    service = InterlinkingService(vault)
    service.discover()
    
    # Should contain filename
    assert service.code_map["NPG/D(74)2"]["English"] == "doc.md"
    # Should also populate bibtex_map
    assert service.bibtex_map["NPG-D-74-2"]["English"] == "doc.md"

def test_interlink_body_protection():
    service = InterlinkingService(Path("/tmp"))
    service.code_map = {"CODE1": {"English": "doc1.md"}}
    
    content = """
archive_code: CODE1
> | ≡&nbsp;archive_code: | CODE1 |
See CODE1.
"""
    # interlink_body should skip lines with 'archive_code:'
    new_content, codes = service.interlink_body(content, "English")
    
    assert "archive_code: CODE1" in new_content
    assert "≡&nbsp;archive_code: | CODE1 |" in new_content
    assert "See [CODE1](doc1.md)." in new_content
    assert "CODE1" in codes

def test_interlink_metadata():
    service = InterlinkingService(Path("/tmp"))
    service.code_map = {
        "CODE1": {"English": "en1.md"},
        "CODE2": {"French": "fr2.md"}
    }
    
    content = """> [!info] Metadata
> | ≡&nbsp;archive_code: | CODE1 |
> | ≡&nbsp;language: | English |
> | ☰&nbsp;references: | CODE2 |

Body text.
"""
    # CODE2 should resolve to fr2.md
    # Pass current_filename as en1.md to prevent self-link in language_versions
    new_content = service.interlink_metadata(content, "English", current_filename="en1.md")
    assert "[CODE2](fr2.md)" in new_content
    assert "language_versions" not in new_content

def test_interlink_metadata_with_lang_versions():
    service = InterlinkingService(Path("/tmp"))
    service.code_map = {
        "CODE1": {"English": "en1.md", "French": "fr1.md"},
    }
    
    content = """> [!info] Metadata
> | ≡&nbsp;archive_code: | CODE1 |
> | ≡&nbsp;language: | English |
"""
    # Should only show French as English is current
    new_content = service.interlink_metadata(content, "English", current_filename="en1.md")
    assert "| ≡&nbsp;language_versions: | [French](fr1.md) |" in new_content

def test_interlink_body_idempotency():
    service = InterlinkingService(Path("/tmp"))
    service.code_map = {
        "CODE1": {"English": "en1.md"}
    }
    
    # 1. Raw code
    content = "See CODE1 for details."
    linked, _ = service.interlink_body(content, "English")
    assert linked == "See [CODE1](en1.md) for details."
    
    # 2. Already linked
    double_linked, _ = service.interlink_body(linked, "English")
    assert double_linked == "See [CODE1](en1.md) for details."

def test_interlink_body_force():
    service = InterlinkingService(Path("/tmp"))
    service.code_map = {
        "CODE1": {"English": "old.md"}
    }
    service.bibtex_map = {
        "CODE1": {"English": "old.md"}
    }
    service.bib_to_norm = {"CODE1": "CODE1"}
    
    content = "See [CODE1](old.md)."
    
    # 1. Update map
    service.code_map["CODE1"] = {"English": "new.md"}
    service.bibtex_map["CODE1"] = {"English": "new.md"}
    
    # 2. Normal interlink (should preserve old link)
    linked, _ = service.interlink_body(content, "English", force=False)
    assert linked == "See [CODE1](old.md)."
    
    # 3. Force interlink (should update to new link)
    forced, _ = service.interlink_body(content, "English", force=True)
    assert forced == "See [CODE1](new.md)."
    
    # 4. Self-link removal on force
    content_self = "See [CODE1](new.md)."
    forced_self, _ = service.interlink_body(content_self, "English", current_filename="new.md", force=True)
    assert forced_self == "See CODE1."

def test_self_reference_removal():
    service = InterlinkingService(Path("/tmp"))
    # Document is CODE1
    content = """> [!info] Metadata
> | ≡&nbsp;archive_code: | CODE1 |
> | ≡&nbsp;language: | English |
> | ☰&nbsp;references: | CODE1, CODE2 |
"""
    service.code_map = {"CODE2": {"English": "doc2.md"}}
    
    # CODE1 should be removed from references (self-reference)
    new_content = service.interlink_metadata(content, "English", current_filename="en1.md")
    assert "references: | [CODE2](doc2.md) |" in new_content
    assert "CODE1" not in new_content.split("references:")[1]
