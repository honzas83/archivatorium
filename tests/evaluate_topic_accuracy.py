import logging
from pathlib import Path

import click

from ocrpolish.services.ollama_client import OllamaClient
from ocrpolish.services.topics_service import TopicExtractor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option("-h", "--hierarchy-file", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--model", default="gemma4:26b")
def evaluate(input_file: Path, hierarchy_file: Path, model: str):
    """Simple evaluation script to compare extraction methods."""
    client = OllamaClient(model=model)
    content = input_file.read_text(encoding="utf-8")
    
    # 1. Two-step extraction
    logger.info("Running two-step extraction...")
    extractor_two_step = TopicExtractor(client, hierarchy_file, flat_mode=False)
    results_two_step = extractor_two_step.extract_topics(content[:10000])
    
    # 2. Flat extraction
    logger.info("Running flat extraction...")
    extractor_flat = TopicExtractor(client, hierarchy_file, flat_mode=True)
    results_flat = extractor_flat.extract_topics(content[:10000])
    
    click.echo("\n" + "="*40)
    click.echo(f"Evaluation for: {input_file.name}")
    click.echo("="*40)
    
    click.echo("\n[Two-Step Method Results]")
    for a in results_two_step:
        click.echo(f"- {a.category}/{a.topic}: {a.reason[:100]}...")
        
    click.echo("\n[Flat Method Results]")
    for a in results_flat:
        click.echo(f"- {a.category}/{a.topic}: {a.reason[:100]}...")
    
    click.echo("\n" + "="*40)

if __name__ == "__main__":
    evaluate()
