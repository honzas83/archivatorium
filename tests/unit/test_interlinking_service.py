from pathlib import Path

from ocrpolish.services.interlinking_service import InterlinkingService


def test_service_initialization():
    vault_dir = Path("/tmp/vault")
    service = InterlinkingService(vault_dir)
    assert service.vault_dir == vault_dir
    assert service.code_map == {}

def test_normalize_code():
    assert InterlinkingService.normalize_code("DPC / D (69) 58") == "DPC/D(69)58"
    assert InterlinkingService.normalize_code("CODE 123") == "CODE123"
    assert InterlinkingService.normalize_code("") == ""
    assert InterlinkingService.normalize_code(None) == ""

def test_resolve_link_priority():
    service = InterlinkingService(Path("/tmp"))
    service.code_map = {
        "CODE1": {
            "English": "path/en.md",
            "French": "path/fr.md",
            "German": "path/de.md"
        }
    }
    
    # Same language
    assert service.resolve_link("CODE1", "French") == "path/fr.md"
    
    # Fallback to English
    assert service.resolve_link("CODE1", "Italian") == "path/en.md"
    
    # Fallback to any (if English missing)
    service.code_map["CODE2"] = {"French": "path/fr2.md"}
    assert service.resolve_link("CODE2", "Italian") == "path/fr2.md"
    
    # Missing code
    assert service.resolve_link("MISSING", "English") is None

def test_interlink_metadata():
    service = InterlinkingService(Path("/tmp"))
    service.code_map = {
        "CODE1": {"English": "path/en1.md"},
        "CODE2": {"French": "path/fr2.md"}
    }
    
    content = """---
language: English
---
> [!info] Metadata
> | ≡&nbsp;archive_code: | CODE1 |
> | ≡&nbsp;language: | English |
> | ☰&nbsp;references: | CODE2 |

Body text.
"""
    # CODE2 should resolve to path/fr2.md
    # language_versions should not appear (only one version of CODE1)
    new_content = service.interlink_metadata(content, "English")
    assert "| [CODE2](path/fr2.md) |" in new_content
    assert "language_versions" not in new_content

def test_interlink_metadata_with_lang_versions():
    service = InterlinkingService(Path("/tmp"))
    service.code_map = {
        "CODE1": {"English": "path/en1.md", "French": "path/fr1.md"},
    }
    
    content = """> [!info] Metadata
> | ≡&nbsp;archive_code: | CODE1 |
> | ≡&nbsp;language: | English |
"""
    new_content = service.interlink_metadata(content, "English")
    assert "| ≡&nbsp;language_versions: | [French](path/fr1.md) |" in new_content

def test_interlink_body_idempotency():
    service = InterlinkingService(Path("/tmp"))
    service.code_map = {
        "CODE1": {"English": "path/en1.md"}
    }
    
    # 1. Raw code
    content = "See CODE1 for details."
    linked = service.interlink_body(content, "English")
    assert linked == "See [CODE1](path/en1.md) for details."
    
    # 2. Already linked
    double_linked = service.interlink_body(linked, "English")
    assert double_linked == "See [CODE1](path/en1.md) for details."
    
    # 3. Code as prefix
    service.code_map["CODE1_REV"] = {"English": "path/rev.md"}
    content = "See CODE1_REV."
    linked = service.interlink_body(content, "English")
    assert linked == "See [CODE1_REV](path/rev.md)."
    assert "CODE1](path/en1.md)_REV" not in linked
