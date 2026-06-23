from pathlib import Path

from archivatorium.services.interlinking_service import InterlinkingService


def test_interlink_body_flexibility() -> None:
    # Mocking a vault directory
    vault_dir = Path("mock_vault")
    service = InterlinkingService(vault_dir)

    # Manually populate maps to simulate indexed vault
    # Canonical code: NPG/D(73)15
    # File: NPG-D(73)15_ENG.md
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
    Reference to (1) NPG/D(73)/15 and (2) NPG/D(73)16.
    Also NPG-D-73-15.
    And NPG/D(73) /15 (with space).
    And NPG-D(73)15 (mixed separators).
    And NPG D(73) 15 (only spaces).
    And NPGD(73)15 (no separators).
    """

    # Current implementation of interlink_body
    new_body, found = service.interlink_body(body, "English", "Current.md")

    print(f"Found codes: {found}")
    print(f"New body:\n{new_body}")

    # We want to find NPG/D(73)15 at least 5 times in various forms
    assert "NPG/D(73)15" in found
    assert "NPG/D(73)16" in found

    assert "[NPG/D(73)/15](NPG-D(73)15_ENG.md)" in new_body
    assert "[NPG/D(73)16](NPG-D(73)16_ENG.md)" in new_body
    assert "[NPG-D-73-15](NPG-D(73)15_ENG.md)" in new_body
    assert "[NPG/D(73) /15](NPG-D(73)15_ENG.md)" in new_body
    assert "[NPG-D(73)15](NPG-D(73)15_ENG.md)" in new_body
    assert "[NPG D(73) 15](NPG-D(73)15_ENG.md)" in new_body
    # NPGD(73)15 has no separators, so its bibkey NPGD-73-15 does not match NPG-D-73-15. It stays as text.
    assert "NPGD(73)15 (no separators)" in new_body


if __name__ == "__main__":
    test_interlink_body_flexibility()
