from pathlib import Path

from archivatorium.services.interlinking_service import InterlinkingService


def test_service_initialization() -> None:
    vault_dir = Path("/tmp/vault")
    service = InterlinkingService(vault_dir)
    assert service.vault_dir == vault_dir
    assert service.code_map == {}
    assert service.bibtex_map == {}


def test_normalize_code(tmp_path: Path) -> None:
    service = InterlinkingService(tmp_path)
    assert service.normalize_code("DPC / D (69) 58") == "DPC/D(69)58"
    assert service.normalize_code("CODE-123") == "CODE/123"
    assert service.normalize_code("") == ""


def test_resolve_link_priority():
    service = InterlinkingService(Path("/tmp"))
    service.code_map = {
        "CODE1": {"English": "path/en.md", "French": "path/fr.md", "German": "path/de.md"}
    }
    service.bibtex_map = {"CODE1": {"French": "path/fr_fuzzy.md", "English": "path/en_fuzzy.md"}}

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
    service.bibtex_map = {"NPG-D-74-2": {"English": "npg-74-2.md"}}

    # Should resolve NPG/D(74)/2 using BibTeX key NPG-D-74-2
    assert service.resolve_link("NPG/D(74)/2", "English") == "npg-74-2.md"


def test_discover_filenames_only(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()

    doc = vault / "doc.md"
    doc.write_text(
        """---
archive_code: NPG/D(74)2
language: English
---
""",
        encoding="utf-8",
    )

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
    service.code_map = {"CODE1": {"English": "en1.md"}, "CODE2": {"French": "fr2.md"}}

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


def test_interlink_metadata_references_use_basename_for_nested_paths():
    service = InterlinkingService(Path("/tmp"))
    nested_target = (
        "NPG - Nuclear Planning Group/3 NPG(STUDY) - Nuclear Planning Study/NPG(STUDY)38_ENG.md"
    )
    service.code_map = {
        "CODE1": {"English": "folder/current.md"},
        "NPG(STUDY)/38": {"English": nested_target},
    }

    content = """> [!info] Metadata
> | ≡&nbsp;archive_code: | CODE1 |
> | ≡&nbsp;language: | English |
> | ☰&nbsp;references: | NPG(STUDY)/38 |

Body text.
"""

    new_content = service.interlink_metadata(
        content,
        "English",
        current_relative_path="folder/current.md",
    )

    assert "[NPG(STUDY)/38](NPG(STUDY)38_ENG.md)" in new_content
    assert f"[NPG(STUDY)/38]({nested_target})" not in new_content


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


def test_interlink_metadata_lang_versions_use_basename_for_nested_paths():
    service = InterlinkingService(Path("/tmp"))
    nested_target = (
        "NPG - Nuclear Planning Group/1 NPG - Nuclear Planning Group/1974/NPG-D(74)12_FRE.md"
    )
    service.code_map = {
        "NPG/D(74)12": {
            "English": "NPG - Nuclear Planning Group/1 NPG - Nuclear Planning Group/1974/"
            "NPG-D(74)12_ENG.md",
            "French": nested_target,
        },
    }

    content = """> [!info] Metadata
> | ≡&nbsp;archive_code: | NPG/D(74)12 |
> | ≡&nbsp;language: | English |
"""

    new_content = service.interlink_metadata(
        content,
        "English",
        current_relative_path=service.code_map["NPG/D(74)12"]["English"],
    )

    assert "[French](NPG-D(74)12_FRE.md)" in new_content
    assert f"[French]({nested_target})" not in new_content


def test_interlink_metadata_lang_versions_preserve_filename_punctuation():
    service = InterlinkingService(Path("/tmp"))
    service.code_map = {
        "CODE1": {
            "English": "folder/CODE1_ENG.md",
            "French": "folder/archive/NPG-D(74)12_FRE_final-v2.md",
        },
    }

    content = """> [!info] Metadata
> | ≡&nbsp;archive_code: | CODE1 |
> | ≡&nbsp;language: | English |
"""

    new_content = service.interlink_metadata(
        content,
        "English",
        current_relative_path="folder/CODE1_ENG.md",
    )

    assert "[French](NPG-D(74)12_FRE_final-v2.md)" in new_content


def test_interlink_body_idempotency():
    service = InterlinkingService(Path("/tmp"))
    service.code_map = {"CODE1": {"English": "en1.md"}}

    # 1. Raw code
    content = "See CODE1 for details."
    linked, _ = service.interlink_body(content, "English")
    assert linked == "See [CODE1](en1.md) for details."

    # 2. Already linked
    double_linked, _ = service.interlink_body(linked, "English")
    assert double_linked == "See [CODE1](en1.md) for details."


def test_interlink_body_uses_basename_for_nested_document_links():
    service = InterlinkingService(Path("/tmp"))
    nested_target = (
        "NPG - Nuclear Planning Group/3 NPG(STUDY) - Nuclear Planning Study/NPG(STUDY)38_ENG.md"
    )
    service.code_map = {"NPG(STUDY)/38": {"English": nested_target}}
    service.bibtex_map = {"NPG-STUDY-38": {"English": nested_target}}
    service.bib_to_norm = {"NPG-STUDY-38": "NPG(STUDY)/38"}

    linked, found = service.interlink_body(
        "See NPG(STUDY)/38 for details.",
        "English",
        current_relative_path="folder/current.md",
    )

    assert linked == "See [NPG(STUDY)/38](NPG(STUDY)38_ENG.md) for details."
    assert found == ["NPG(STUDY)/38"]


def test_interlink_body_force():
    service = InterlinkingService(Path("/tmp"))
    service.code_map = {"CODE1": {"English": "old.md"}}
    service.bibtex_map = {"CODE1": {"English": "old.md"}}
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
    forced_self, _ = service.interlink_body(
        content_self, "English", current_filename="new.md", force=True
    )
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


def test_clean_citekey():
    service = InterlinkingService(Path("/tmp"))
    assert service.clean_citekey("[NPG-D-73-6](NPG-D(73)6_FRE.md)_ENG") == "NPG-D-73-6_ENG"
    assert service.clean_citekey("[NPG-WP-73-1](NPG-WP(73)1_ENG.md)-COR1_ENG") == "NPG-WP-73-1-COR1_ENG"
    assert service.clean_citekey("NPG-D-73-6_FRE") == "NPG-D-73-6_FRE"
    assert service.clean_citekey("") == ""


def test_clean_citation_callout():
    service = InterlinkingService(Path("/tmp"))
    dirty_citation = (
        "> [!citing this document]\n"
        "> https://nato-obsidian.kky.zcu.cz/[NPG-D-73-6](NPG-D(73)6_FRE.md)_ENG\n"
        "> @misc{[NPG-WP-73-1](NPG-WP(73)1_ENG.md)-COR1_ENG,\n"
    )
    expected = (
        "> [!citing this document]\n"
        "> https://nato-obsidian.kky.zcu.cz/NPG-D-73-6_ENG\n"
        "> @misc{NPG-WP-73-1-COR1_ENG,\n"
    )
    assert service.clean_citation_callout(dirty_citation) == expected


def test_infer_archive_code():
    service = InterlinkingService(Path("/tmp"))
    assert service.infer_archive_code("NPG-D(73)6_ENG.md") == "NPG/D(73)6"
    assert service.infer_archive_code("NPG-WP(73)1-COR1_FRE.md") == "NPG/WP(73)1-COR1"
    assert service.infer_archive_code("MC-D(75)2_BIL.md") == "MC/D(75)2"
    assert service.infer_archive_code("SomeOtherFile.md") == "SomeOtherFile"


def test_split_body_parts():
    service = InterlinkingService(Path("/tmp"))
    content = (
        "> [!info] Metadata\n"
        "> | key | val |\n"
        "\n"
        "> [!abstract]\n"
        "> Summary and tags\n"
        "\n"
        "# Page 1\n"
        "Document body\n"
        "\n"
        "> [!citing this document]\n"
        "> Citation info\n"
    )
    metadata, abstract, body, citation = service.split_body_parts(content)
    assert metadata == "> [!info] Metadata\n> | key | val |\n"
    assert abstract == "> [!abstract]\n> Summary and tags\n"
    assert body == "\n\n# Page 1\nDocument body\n\n"
    assert citation == "> [!citing this document]\n> Citation info\n"


def test_interlink_all_restores_and_cleans(tmp_path: Path):
    # Setup two language versions: one French with archive_code, one English missing archive_code and with broken citekey
    vault = tmp_path / "vault"
    vault.mkdir()
    
    eng_file = vault / "NPG-D(73)6_ENG.md"
    eng_file.write_text(
        """---
title: ENG Title
citekey: '[NPG-D-73-6](NPG-D(73)6_FRE.md)_ENG'
language: English
---

> [!info] Metadata
> | ≡&nbsp;title: | ENG Title |
> | ≡&nbsp;citekey: | [NPG-D-73-6](NPG-D(73)6_FRE.md)_ENG |
> | ≡&nbsp;language: | English |

# Page 1
Document body content.

> [!citing this document]
> Chicago:
> https://nato-obsidian.kky.zcu.cz/[NPG-D-73-6](NPG-D(73)6_FRE.md)_ENG
""",
        encoding="utf-8"
    )

    fre_file = vault / "NPG-D(73)6_FRE.md"
    fre_file.write_text(
        """---
title: FRE Title
archive_code: NPG/D(73)6
citekey: NPG-D-73-6_FRE
language: French
---

> [!info] Metadata
> | ≡&nbsp;title: | FRE Title |
> | ≡&nbsp;archive_code: | NPG/D(73)6 |
> | ≡&nbsp;citekey: | NPG-D-73-6_FRE |
> | ≡&nbsp;language: | French |

# Page 1
Document body content.

> [!citing this document]
> Chicago:
> https://nato-obsidian.kky.zcu.cz/NPG-D-73-6_FRE
""",
        encoding="utf-8"
    )

    service = InterlinkingService(vault)
    service.discover()
    
    # Verify discover inferred archive_code for ENG file
    assert service.code_map["NPG/D(73)6"]["English"] == "NPG-D(73)6_ENG.md"
    assert service.code_map["NPG/D(73)6"]["French"] == "NPG-D(73)6_FRE.md"

    # Run interlink_all
    service.interlink_all(force=True)

    # Read back the files and verify they are correctly cleaned and cross-linked
    eng_content = eng_file.read_text(encoding="utf-8")
    assert "archive_code: NPG/D(73)6" in eng_content
    assert "citekey: NPG-D-73-6_ENG" in eng_content
    assert "language_versions: | [French](NPG-D(73)6_FRE.md) |" in eng_content
    assert "citekey: | NPG-D-73-6_ENG |" in eng_content
    assert "https://nato-obsidian.kky.zcu.cz/NPG-D-73-6_ENG" in eng_content
    assert "[NPG-D-73-6]" not in eng_content

