from pathlib import Path

import click

from ocrpolish.core import run_processing
from ocrpolish.data_model import ProcessingConfig
from ocrpolish.processor_metadata import MetadataProcessor
from ocrpolish.services.indexing_service import IndexEntry, IndexingService
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
@click.option(
    "--docx",
    type=click.Path(path_type=Path),
    help="Path to generate DOCX files alongside MD.",
)
@click.option(
    "--filter-file",
    type=click.Path(path_type=Path),
    help="Path to a text file containing phrases to filter out.",
)
def clean(  # noqa: PLR0913
    input_dir: Path,
    output_dir: Path,
    mask: str,
    width: int,
    dry_run: bool,
    save_filtered: bool,
    frequency_file: Path,
    docx: Path | None,
    filter_file: Path | None,
) -> None:
    """Post-process OCR Markdown files (wrapping, filtering boilerplate)."""
    config = ProcessingConfig(
        input_dir=input_dir,
        output_dir=output_dir,
        input_mask=mask,
        typewriter_width=width,
        dry_run=dry_run,
        save_filtered=save_filtered,
        frequency_file_path=frequency_file,
        docx_output_dir=docx,
        filter_file_path=filter_file,
    )
    run_processing(config)


@cli.command()
@click.argument("input_dir", type=click.Path(exists=True, path_type=Path))
@click.argument("output_dir", type=click.Path(path_type=Path))
@click.option("--mask", default="*.md", help="Glob pattern for files to process (default: *.md).")
@click.option("--model", default="gemma4:31b", help="Ollama model to use.")
@click.option(
    "--pdf-dir", type=click.Path(path_type=Path), help="Directory containing source PDFs."
)
@click.option("--vault-root", type=click.Path(path_type=Path), help="Root of the Obsidian vault.")
@click.option(
    "--hierarchy-file",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to themes/taxonomy YAML.",
)
@click.option(
    "--tags-file",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to useful tags YAML.",
)
@click.option(
    "--citekey-mode",
    type=click.Choice(["stem", "path"]),
    default="stem",
    show_default=True,
    help="Deterministic citekey generation mode.",
)
@click.option("--overwrite", is_flag=True, help="Overwrite existing output files.")
@click.option("--dry-run", is_flag=True, help="If set, logs metadata without writing files.")
def metadata(  # noqa: PLR0913
    input_dir: Path,
    output_dir: Path,
    mask: str,
    model: str,
    pdf_dir: Path | None,
    vault_root: Path | None,
    hierarchy_file: Path,
    tags_file: Path,
    citekey_mode: str,
    overwrite: bool,
    dry_run: bool,
) -> None:
    """Extract metadata using Ollama and generate sidecar YAML files."""
    effective_vault_root = vault_root or output_dir
    effective_pdf_dir = pdf_dir or output_dir

    template_dir = Path("obsidian_template")
    if template_dir.exists() and not dry_run:
        initialize_vault_from_template(template_dir, output_dir)

    ollama_client = OllamaClient(model=model)
    windowing_service = SlidingWindowService()
    tagging_service = TaggingService(
        ollama_client=ollama_client,
        windowing_service=windowing_service,
        themes_path=hierarchy_file,
        useful_tags_path=tags_file,
        model_name=model,
    )

    processor = MetadataProcessor(
        ollama_client=ollama_client,
        output_dir=output_dir,
        overwrite=overwrite,
        vault_root=effective_vault_root,
        pdf_dir=effective_pdf_dir,
        tagging_service=tagging_service,
        input_dir=input_dir,
        citekey_mode=citekey_mode,
    )
    processor.preflight_scan()

    matching_markdown = set(processor.get_files(input_dir, mask=mask, all_files=False))
    files = sorted(processor.get_files(input_dir, mask=mask, all_files=True))
    if not files:
        click.echo("No files found to process.")
        return

    with click.progressbar(files, label="Processing files") as bar:
        for input_file in bar:
            relative_path = input_file.relative_to(input_dir)
            output_file = output_dir / relative_path

            try:
                is_md = input_file.suffix.lower() == ".md"
                is_filtered = input_file.name.endswith(".filtered.md")
                is_pdf = input_file.suffix.lower() == ".pdf"

                if dry_run:
                    click.echo(f"\n[DRY-RUN] Would consider {relative_path}")
                    continue

                if is_md and not is_filtered and input_file in matching_markdown:
                    # Get 50 most frequent tags
                    frequent_tags = [
                        tag for tag, _ in processor.conceptual_tag_counts.most_common(50)
                    ]
                    processor.process_file(input_file, output_file, frequent_tags)
                elif is_md and not is_filtered:
                    mirror_file(input_file, output_file)
                elif is_pdf:
                    pdf_output_file = processor.get_mirrored_pdf_path(input_file)
                    if pdf_output_file.exists() and not pdf_output_file.samefile(input_file):
                        raise ValueError(
                            f"Ambiguous mirrored PDF target already exists: {pdf_output_file}"
                        )
                    mirror_file(input_file, pdf_output_file)
                else:
                    mirror_file(input_file, output_file)
            except Exception as e:
                click.echo(f"\nError processing {relative_path}: {e}", err=True)


@cli.command()
@click.argument("input_dir", type=click.Path(exists=True, path_type=Path))
@click.argument("output_dir", type=click.Path(path_type=Path))
@click.option("--mask", default="*.md", help="Glob pattern for files to process (default: *.md).")
@click.option("--template-dir", type=click.Path(exists=True, path_type=Path), required=True)
def obsidian(input_dir: Path, output_dir: Path, mask: str, template_dir: Path) -> None:
    """Generate an Obsidian vault from processed Markdown and metadata."""
    initialize_vault_from_template(template_dir, output_dir)
    # Mirroring logic has been integrated into the metadata pass directly.
    # Leaving command as placeholder or for pure template init.



@cli.command()
@click.argument("vault_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--dry-run", is_flag=True, help="If set, logs changes without writing to files.")
@click.option("--verbose", is_flag=True, help="Show detailed matching logs.")
@click.option("--force", is_flag=True, help="Regenerate all links, even if they already exist.")
@click.option(
    "--unifications",
    type=click.Path(exists=True, path_type=Path),
    help="Path to custom unification rules YAML.",
)
def interlink(
    vault_dir: Path, dry_run: bool, verbose: bool, force: bool, unifications: Path | None
) -> None:
    """Post-processes a generated Obsidian vault in-place to interlink documents, generate indices, and export metadata."""

    service = InterlinkingService(vault_dir, unifications_path=unifications)

    click.echo(f"Scanning vault: {vault_dir}")
    service.discover()

    click.echo(f"Interlinking {len(service.code_map)} unique archive codes...")
    service.interlink_all(dry_run=dry_run, verbose=verbose, force=force)

    click.echo("Generating Markdown indices and XLSX export...")
    # Map final (potentially updated) VaultDocuments to IndexEntries
    indexer = IndexingService(vault_dir)
    for doc in service.documents:
        entry = IndexEntry(
            doc_path=Path(doc.vault_relative_path),
            title=doc.frontmatter.get("title", doc.path.stem),
            summary=doc.frontmatter.get("summary", ""),
            date=doc.frontmatter.get("date", ""),
            raw_metadata=doc.frontmatter,
            canonical_tags=doc.canonical_tags,
        )
        indexer.entries.append(entry)

    if not dry_run:
        # Generate outputs in VAULT_DIR
        indexer.generate_xlsx(vault_dir / "metadata_index.xlsx")
        indexer.generate_markdown_indices()
    else:
        click.echo("[DRY-RUN] Would generate index files and metadata_index.xlsx")

    click.echo("Done.")


@cli.command()
@click.argument("input_dir", type=click.Path(exists=True, path_type=Path))
@click.argument("output_dir", type=click.Path(path_type=Path))
@click.option("--host", help="Ollama server URL.")
@click.option("--user", help="DigestAuth username.")
@click.option("--password", help="DigestAuth password.")
@click.option("--model", default="qwen3.5:9b", show_default=True, help="VLM model to use.")
@click.option("--dpi", type=int, default=300, show_default=True, help="DPI for page rendering.")
@click.option(
    "--no-page-header",
    is_flag=True,
    help="Do not include Page headers in the output.",
)
def ocr(  # noqa: PLR0913
    input_dir: Path,
    output_dir: Path,
    host: str | None,
    user: str | None,
    password: str | None,
    model: str,
    dpi: int,
    no_page_header: bool,
) -> None:
    """OCR multipage PDF files using Ollama (VLM) → Markdown."""
    from ocrpolish.ocr_engine import OCREngine

    engine = OCREngine(
        host=host,
        user=user,
        password=password,
        model=model,
        dpi=dpi,
    )

    # Recursively find pdf files
    pdf_files = sorted(list(input_dir.rglob("*")))
    pdf_files = [f for f in pdf_files if f.is_file() and f.suffix.lower() == ".pdf"]

    if not pdf_files:
        click.echo(f"No PDF files found in {input_dir}")
        return

    click.echo(f"Found {len(pdf_files)} PDF files to process.")
    with click.progressbar(pdf_files, label="Processing PDFs") as bar:
        for pdf_file in bar:
            rel_path = pdf_file.relative_to(input_dir)
            output_md = output_dir / rel_path.with_suffix(".md")
            try:
                engine.run_ocr(
                    input_pdf=pdf_file,
                    output_md=output_md,
                    page_header=not no_page_header,
                )
            except Exception as e:
                click.echo(f"\nError processing {rel_path}: {e}", err=True)


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
