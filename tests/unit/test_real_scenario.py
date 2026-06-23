from pathlib import Path

from archivatorium.services.interlinking_service import InterlinkingService


def test_real_file_scenario() -> None:
    # Mocking a vault directory
    vault_dir = Path("mock_vault_real")
    vault_dir.mkdir(exist_ok=True)

    service = InterlinkingService(vault_dir)

    # Target files
    service.code_map = {
        "NPG/D(73)15": {"English": "NPG-D(73)15_ENG.md"},
        "NPG/D(73)16": {"English": "NPG-D(73)16_ENG.md"},
    }
    service.bibtex_map = {
        "NPG-D-73-15": {"English": "NPG-D(73)15_ENG.md"},
        "NPG-D-73-16": {"English": "NPG-D(73)16_ENG.md"},
    }
    service.bib_to_norm = {"NPG-D-73-15": "NPG/D(73)15", "NPG-D-73-16": "NPG/D(73)16"}

    body = """
(1) NPG/D(73)/15, 16th October, 1973, Annex, paragraph 5
(2) NPG/D(73)/15, paragraph 5

(1) NPG/D(73)/16, 8th November, 1973, paragraph 30
    """

    new_body, found = service.interlink_body(body, "English", "NPG-D(74)3_ENG.md")

    print(f"Found codes: {found}")
    print(f"New body:\n{new_body}")

    assert "[NPG/D(73)/15](NPG-D(73)15_ENG.md)" in new_body
    assert "[NPG/D(73)/16](NPG-D(73)16_ENG.md)" in new_body


if __name__ == "__main__":
    test_real_file_scenario()
