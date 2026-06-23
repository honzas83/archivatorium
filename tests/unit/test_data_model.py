from pathlib import Path

from archivatorium.data_model import ProcessingConfig


def test_config_defaults() -> None:
    config = ProcessingConfig(input_dir=Path("input"), output_dir=Path("output"))
    assert config.input_dir == Path("input")
    assert config.output_dir == Path("output")
    assert config.input_mask == "*.md"
    assert config.typewriter_width == 80  # noqa: PLR2004
    assert config.save_filtered is True


def test_config_custom() -> None:
    config = ProcessingConfig(
        input_dir=Path("input"),
        output_dir=Path("output"),
        input_mask="*.txt",
        typewriter_width=100,
        save_filtered=False,
    )
    assert config.input_mask == "*.txt"
    assert config.typewriter_width == 100  # noqa: PLR2004
    assert config.save_filtered is False
