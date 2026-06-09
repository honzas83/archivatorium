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
