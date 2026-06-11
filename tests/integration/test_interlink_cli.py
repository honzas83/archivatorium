from click.testing import CliRunner

from ocrpolish.cli import cli


def test_interlink_command_exists():
    runner = CliRunner()
    result = runner.invoke(cli, ["interlink", "--help"])
    assert result.exit_code == 0
    assert "Post-processes a generated Obsidian vault" in result.output


def test_full_vault_interlinking(tmp_path):
    # Setup a small vault
    vault = tmp_path / "vault"
    vault.mkdir()

    doc1 = vault / "doc1.md"
    doc1.write_text(
        """---
archive_code: CODE1
language: English
---
> [!info] Metadata
> | ≡&nbsp;archive_code: | CODE1 |
> | ≡&nbsp;language: | English |
> | ☰&nbsp;references: | CODE2 |

See CODE2 for more info.
""",
        encoding="utf-8",
    )

    doc2 = vault / "doc2.md"
    doc2.write_text(
        """---
archive_code: CODE2
language: French
---
> [!info] Metadata
> | ≡&nbsp;archive_code: | CODE2 |
> | ≡&nbsp;language: | French |
> | ☰&nbsp;references: | CODE1 |

Regardez CODE1.
""",
        encoding="utf-8",
    )

    doc1_fr = vault / "doc1_fr.md"
    doc1_fr.write_text(
        """---
archive_code: CODE1
language: French
---
> [!info] Metadata
> | ≡&nbsp;archive_code: | CODE1 |
> | ≡&nbsp;language: | French |
""",
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["interlink", str(vault)])
    assert result.exit_code == 0

    # Check doc1
    c1 = doc1.read_text(encoding="utf-8")
    # References should link to doc2 (French version is only version)
    assert "[CODE2](doc2.md)" in c1
    # Body should link
    assert "See [CODE2](doc2.md)" in c1
    # Language versions should show French version of CODE1
    assert "language_versions: | [French](doc1_fr.md)" in c1

    # Check doc2
    c2 = doc2.read_text(encoding="utf-8")
    # References should link to doc1_fr (same language priority)
    assert "[CODE1](doc1_fr.md)" in c2
    # Body should link
    assert "Regardez [CODE1](doc1_fr.md)" in c2


def test_interlink_export_uses_canonical_tags_only(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    doc = vault / "doc.md"
    doc.write_text(
        """---
archive_code: CODE1
language: English
---
#State/Belgium #Org/NATO #Entities/Org/SHAPE #Tags/Canonical
""",
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["interlink", str(vault)])

    assert result.exit_code == 0
    assert (vault / "Index - Organizations.md").exists()
    assert not (vault / "Index - States.md").exists()
    xlsx = vault / "metadata_index.xlsx"
    assert xlsx.exists()


def test_interlink_language_versions_use_filename_for_nested_siblings(tmp_path):
    vault = tmp_path / "vault"
    doc_dir = vault / "NPG - Nuclear Planning Group" / "1 NPG - Nuclear Planning Group" / "1974"
    doc_dir.mkdir(parents=True)

    english = doc_dir / "NPG-D(74)12_ENG.md"
    english.write_text(
        """---
archive_code: NPG/D(74)12
language: English
---
> [!info] Metadata
> | ≡&nbsp;archive_code: | NPG/D(74)12 |
> | ≡&nbsp;language: | English |
""",
        encoding="utf-8",
    )

    french = doc_dir / "NPG-D(74)12_FRE.md"
    french.write_text(
        """---
archive_code: NPG/D(74)12
language: French
---
> [!info] Metadata
> | ≡&nbsp;archive_code: | NPG/D(74)12 |
> | ≡&nbsp;language: | French |
""",
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["interlink", str(vault)])

    assert result.exit_code == 0
    content = english.read_text(encoding="utf-8")
    assert "[French](NPG-D(74)12_FRE.md)" in content
    assert "[French](NPG - Nuclear Planning Group/" not in content


def test_interlink_references_and_body_use_filename_for_nested_targets(tmp_path):
    vault = tmp_path / "vault"
    source_dir = vault / "NPG - Nuclear Planning Group" / "1 NPG - Nuclear Planning Group"
    target_dir = vault / "NPG - Nuclear Planning Group" / "3 NPG(STUDY) - Nuclear Planning Study"
    source_dir.mkdir(parents=True)
    target_dir.mkdir(parents=True)

    source = source_dir / "NPG-D(74)12_ENG.md"
    source.write_text(
        """---
archive_code: NPG/D(74)12
language: English
---
> [!info] Metadata
> | ≡&nbsp;archive_code: | NPG/D(74)12 |
> | ≡&nbsp;language: | English |
> | ☰&nbsp;references: | NPG(STUDY)/38 |

See NPG(STUDY)/38 for details.
""",
        encoding="utf-8",
    )

    target = target_dir / "NPG(STUDY)38_ENG.md"
    target.write_text(
        """---
archive_code: NPG(STUDY)/38
language: English
---
> [!info] Metadata
> | ≡&nbsp;archive_code: | NPG(STUDY)/38 |
> | ≡&nbsp;language: | English |
""",
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["interlink", str(vault)])

    assert result.exit_code == 0
    content = source.read_text(encoding="utf-8")
    assert "[NPG(STUDY)/38](NPG(STUDY)38_ENG.md)" in content
    assert "[NPG(STUDY)/38](NPG - Nuclear Planning Group/" not in content
