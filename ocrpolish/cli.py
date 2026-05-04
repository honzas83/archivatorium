import sys
from pathlib import Path

import click

from ocrpolish.core import run_processing
from ocrpolish.data_model import ProcessingConfig
from ocrpolish.processor_metadata import MetadataProcessor
from ocrpolish.services.indexing_service import IndexingService
from ocrpolish.services.ollama_client import OllamaClient
from ocrpolish.services.topics_service import TopicExtractor
from ocrpolish.utils.logging import setup_logging


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
@click.option(
    "--filter-file",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to a file containing patterns to exclude.",
)
@click.option(
    "--docx",
    "docx_output_dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Generate DOCX files in the specified directory.",
)
@click.option(
    "--scan-paragraphs",
    default=3,
    type=int,
    help="Number of paragraphs at top/bottom to scan for headers/footers (default: 3).",
)
def clean(
    input_dir: Path,
    output_dir: Path,
    mask: str,
    width: int,
    dry_run: bool,
    save_filtered: bool,
    frequency_file: Path,
    filter_file: Path,
    docx_output_dir: Path,
    scan_paragraphs: int,
) -> None:
    """Clean LLM-OCR output by removing headers/footers and reformatting paragraphs."""
    config = ProcessingConfig(
        input_dir=input_dir,
        output_dir=output_dir,
        input_mask=mask,
        typewriter_width=width,
        dry_run=dry_run,
        save_filtered=save_filtered,
        frequency_file_path=frequency_file,
        filter_file_path=filter_file,
        docx_output_dir=docx_output_dir,
        scan_paragraphs=scan_paragraphs,
    )
    try:
        run_processing(config)
    except Exception as e:
        click.echo(f"Error during cleaning: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("input_dir", type=click.Path(exists=True, path_type=Path))
@click.argument("output_dir", type=click.Path(path_type=Path))
@click.option(
    "--model", default="gemma4:26b", help="The Ollama model to use. (Default: gemma4:26b)"
)
@click.option(
    "--recursive/--no-recursive",
    default=True,
    help="Whether to process subdirectories. (Default: recursive)",
)
@click.option(
    "--ollama-url",
    default="http://localhost:11434",
    help="The URL of the Ollama server. (Default: http://localhost:11434)",
)
@click.option(
    "--overwrite/--no-overwrite",
    default=False,
    help="Whether to overwrite existing files in the output directory. (Default: no-overwrite)",
)
@click.option("--dry-run", is_flag=True, help="If set, logs the metadata without writing files.")
@click.option(
    "--vault-root",
    type=click.Path(path_type=Path),
    default=None,
    help="Root directory of the Obsidian vault for relative link calculation.",
)
@click.option(
    "--pdf-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory containing source PDF files (if different from input_dir).",
)
@click.option(
    "--hierarchy-file",
    "-h",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Optional path to a YAML topic hierarchy for topic extraction.",
)
@click.option(
    "--flat-topics",
    is_flag=True,
    help="Perform single-step flat topic extraction instead of two-step.",
)
def metadata(  # noqa: PLR0913
    input_dir: Path,
    output_dir: Path,
    model: str,
    recursive: bool,
    ollama_url: str,
    overwrite: bool,
    dry_run: bool,
    vault_root: Path | None,
    pdf_dir: Path | None,
    hierarchy_file: Path | None,
    flat_topics: bool,
) -> None:
    """Extracts metadata from Markdown files using a local Ollama instance."""
    client = OllamaClient(model=model, host=ollama_url)
    
    topic_extractor = None
    if hierarchy_file:
        topic_extractor = TopicExtractor(
            client, 
            hierarchy_file, 
            flat_mode=flat_topics
        )

    processor = MetadataProcessor(
        client, 
        output_dir, 
        overwrite=overwrite, 
        vault_root=vault_root, 
        pdf_dir=pdf_dir,
        topic_extractor=topic_extractor
    )

    files = sorted(processor.get_files(input_dir, recursive=recursive))
    if not files:
        click.echo("No markdown files found to process.")
        return

    with click.progressbar(files, label="Extracting metadata") as bar:
        for input_file in bar:
            relative_path = input_file.relative_to(input_dir)
            output_file = output_dir / relative_path

            # TODO: Handle dry-run in processor if needed
            try:
                processor.process_file(input_file, output_file)
            except Exception as e:
                click.echo(f"\nError processing {relative_path}: {e}", err=True)


@cli.command()
@click.argument("input_dir", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output-xlsx",
    "-o",
    type=click.Path(path_type=Path),
    help="Path to save the XLSX metadata index.",
)
@click.option(
    "--topics-yaml",
    "-t",
    type=click.Path(exists=True, path_type=Path),
    help="Path to the YAML file defining topic hierarchy.",
)
@click.option(
    "--recursive/--no-recursive",
    default=True,
    help="Whether to scan subdirectories. (Default: recursive)",
)
def index(
    input_dir: Path,
    output_xlsx: Path | None,
    topics_yaml: Path | None,
    recursive: bool,
) -> None:
    """Generates Obsidian index pages and an optional XLSX index from vault metadata."""
    indexer = IndexingService(input_dir, topics_yaml=topics_yaml)

    click.echo(f"Scanning vault: {input_dir}")
    # Get file list for progress bar
    pattern = "**/*.md" if recursive else "*.md"
    files = [f for f in input_dir.glob(pattern) if not f.name.startswith("Index - ")]
    
    if not files:
        click.echo("No markdown files found to index.")
        return

    with click.progressbar(files, label="Indexing documents") as bar:
        for file_path in bar:
            indexer.process_file(file_path)

    if output_xlsx:
        click.echo(f"Generating XLSX index: {output_xlsx}")
        indexer.generate_xlsx(output_xlsx)

    click.echo("Generating Markdown indices...")
    indexer.generate_markdown_indices()
    click.echo("Done.")


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
