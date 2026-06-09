from pathlib import Path

from ocrpolish.utils.metadata import generate_citekey


def test_generate_citekey_default_stem() -> None:
    # Stem mode is default
    output_file = Path("vault/subfolder/NPG_D(74)2.md")
    key = generate_citekey(output_file)
    assert key == "NPG_D-74-2"


def test_generate_citekey_path_mode_with_vault_root() -> None:
    output_file = Path("vault/subfolder/another_sub/NPG_D(74)2.md")
    vault_root = Path("vault")
    key = generate_citekey(output_file, mode="path", vault_root=vault_root)
    # Output file relative to vault is subfolder/another_sub/NPG_D(74)2.md
    # Stripped suffix, replaced slashes: subfolder:another_sub:NPG_D(74)2
    # Normalized: subfolder-another_sub-NPG_D-74-2
    assert key == "subfolder:another_sub:NPG_D-74-2"


def test_generate_citekey_path_mode_with_output_dir() -> None:
    output_file = Path("out/subfolder/file.md")
    output_dir = Path("out")
    key = generate_citekey(output_file, mode="path", output_dir=output_dir)
    assert key == "subfolder:file"


def test_generate_citekey_path_mode_fallback() -> None:
    # If not inside vault or output_dir, falls back to stem
    output_file = Path("vault/subfolder/file.md")
    key = generate_citekey(output_file, mode="path")
    assert key == "file"
