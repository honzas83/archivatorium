import sys
from pathlib import Path

import click

from ocrpolish.core import run_processing
from ocrpolish.data_model import ProcessingConfig
from ocrpolish.processor_metadata import MetadataProcessor
from ocrpolish.services.indexing_service import IndexingService
from ocrpolish.services.interlinking_service import InterlinkingService
from ocrpolish.services.ollama_client import OllamaClient
from ocrpolish.services.tagging_service import TaggingService
from ocrpolish.services.windowing_service import SlidingWindowService
from ocrpolish.utils.files import initialize_vault_from_template
from ocrpolish.utils.logging import setup_logging
from ocrpolish.utils.metadata import mirror_file


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Increase output verbosity.")
def cli(verbose: bool) -> None:
    """A toolkit for cleaning, formatting, and validating OCR outputs processed by LLMs."""
    setup_logging(verbose=verbose)


@cli.command()
@click.argument("input_dir", type=click.Path(exists=True, path_type=Path))
@click.argument("output_dir", type=click.Path(path_type=Path))
@click.option("--mask", default="*.md", help="Glob pattern for files to process (default: *.md).")
@click.option(
    "--width",
    default=80,
    type=int,
    help="Typewriter width. Lines longer than this are wrapped (default: 80).",
)
@click.option(
    "--dry-run", is_flag=True, help="Identify boilerplate without writing primary output files."
)
@click.option(
    "--no-filtered",
    "save_filtered",
    is_flag=True,
    default=True,
    help="Disable generation of .filtered.md sidecar files.",
)
@click.option(
    "--frequency-file",
    type=click.Path(path_type=Path),
    default=Path("frequency.txt"),
    help="Path for the consolidated frequency report (within output_dir).",
)
def clean(
    input_dir: Path,
    output_dir: Path,
    mask: str,
    width: int,
    dry_run: bool,
    save_filtered: bool,
    frequency_file: Path,
) -> None:
    """Post-process OCR Markdown files (wrapping, filtering boilerplate)."""
    config = ProcessingConfig(
        input_dir=input_dir,
        output_dir=output_dir,
        mask=mask,
        width=width,
        dry_run=dry_run,
        save_filtered=save_filtered,
        frequency_file=frequency_file,
    )
    run_processing(config)


@cli.command()
@click.argument("input_dir", type=click.Path(exists=True, path_type=Path))
@click.argument("output_dir", type=click.Path(path_type=Path))
@click.option("--mask", default="*.md", help="Glob pattern for files to process (default: *.md).")
def metadata(input_dir: Path, output_dir: Path, mask: str) -> None:
    """Extract metadata using Ollama and generate sidecar YAML files."""
    processor = MetadataProcessor(OllamaClient())
    processor.process_directory(input_dir, output_dir, mask)


@cli.command()
@click.argument("input_dir", type=click.Path(exists=True, path_type=Path))
@click.argument("output_dir", type=click.Path(path_type=Path))
@click.option("--mask", default="*.md", help="Glob pattern for files to process (default: *.md).")
@click.option("--template-dir", type=click.Path(exists=True, path_type=Path), required=True)
def obsidian(input_dir: Path, output_dir: Path, mask: str, template_dir: Path) -> None:
    """Generate an Obsidian vault from processed Markdown and metadata."""
    initialize_vault_from_template(template_dir, output_dir)
    for md_file in input_dir.rglob(mask):
        yaml_file = md_file.with_suffix(".yaml")
        if yaml_file.exists():
            mirror_file(md_file, yaml_file, output_dir, input_dir)


@cli.command()
@click.argument("input_dir", type=click.Path(exists=True, path_type=Path))
@click.argument("output_dir", type=click.Path(path_type=Path))
@click.option("--mask", default="*.md", help="Glob pattern for files to process (default: *.md).")
def index(input_dir: Path, output_dir: Path, mask: str) -> None:
    """Index metadata and generate citations."""
    service = IndexingService()
    service.index_directory(input_dir, mask)
    service.generate_citations(output_dir)


@cli.command()
@click.argument("input_dir", type=click.Path(exists=True, path_type=Path))
@click.argument("output_dir", type=click.Path(path_type=Path))
@click.option("--mask", default="*.md", help="Glob pattern for files to process (default: *.md).")
@click.option("--taxonomy", type=click.Path(exists=True, path_type=Path), required=True)
@click.option("--tags", type=click.Path(exists=True, path_type=Path), required=True)
def tag(input_dir: Path, output_dir: Path, mask: str, taxonomy: Path, tags: Path) -> None:
    """Apply tiered tagging system to Obsidian vault."""
    service = TaggingService(taxonomy_path=taxonomy, tags_path=tags)
    service.tag_vault(input_dir, output_dir, mask)


@cli.command()
@click.argument("vault_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--dry-run", is_flag=True, help="If set, logs changes without writing to files.")
@click.option("--verbose", is_flag=True, help="Show detailed matching logs.")
def interlink(vault_dir: Path, dry_run: bool, verbose: bool):
    """Post-processes a generated Obsidian vault in-place to interlink documents."""
    service = InterlinkingService(vault_dir)
    
    click.echo(f"Scanning vault: {vault_dir}")
    service.discover()
    
    click.echo(f"Interlinking {len(service.code_map)} unique archive codes...")
    service.interlink_all(dry_run=dry_run, verbose=verbose)
    
    click.echo("Done.")


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
