#!/usr/bin/env python3
"""
openalex_search_cli - Auto-generated CLI from PRD.md
"""

import click
from src.config import Config

from src.commands.works_commands import works_group
from src.commands.authors_commands import authors_group
from src.commands.sources_commands import sources_group
from src.commands.institutions_commands import institutions_group
from src.commands.topics_commands import topics_group
from src.commands.keywords_commands import keywords_group
from src.commands.publishers_commands import publishers_group
from src.commands.funders_commands import funders_group
from src.commands.autocomplete_commands import autocomplete_group
from src.commands.domains_commands import domains_group
from src.commands.fields_commands import fields_group
from src.commands.subfields_commands import subfields_group
from src.commands.sdgs_commands import sdgs_group
from src.commands.countries_commands import countries_group
from src.commands.continents_commands import continents_group
from src.commands.languages_commands import languages_group
from src.commands.awards_commands import awards_group
from src.commands.changefiles_commands import changefiles_group
from src.commands.rate_limit_commands import rate_limit_group
from src.commands.text_topics_commands import text_topics_group


@click.group()
@click.option('--config', type=click.Path(exists=False), help='Config file path')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, config, verbose):
    """
    Openalex Search Cli - API CLI Client

    API: OpenAlex API Python Client
    Version: `1.0.0`
    """
    ctx.ensure_object(dict)
    ctx.obj['config'] = Config(config_path=config)
    ctx.obj['verbose'] = verbose


# Register resource commands
cli.add_command(works_group, 'works')
cli.add_command(authors_group, 'authors')
cli.add_command(sources_group, 'sources')
cli.add_command(institutions_group, 'institutions')
cli.add_command(topics_group, 'topics')
cli.add_command(keywords_group, 'keywords')
cli.add_command(publishers_group, 'publishers')
cli.add_command(funders_group, 'funders')
cli.add_command(autocomplete_group, 'autocomplete')
cli.add_command(domains_group, 'domains')
cli.add_command(fields_group, 'fields')
cli.add_command(subfields_group, 'subfields')
cli.add_command(sdgs_group, 'sdgs')
cli.add_command(countries_group, 'countries')
cli.add_command(continents_group, 'continents')
cli.add_command(languages_group, 'languages')
cli.add_command(awards_group, 'awards')
cli.add_command(changefiles_group, 'changefiles')
cli.add_command(rate_limit_group, 'rate_limit')
cli.add_command(text_topics_group, 'text_topics')


@cli.command()
@click.option('--format', type=click.Choice(['json', 'csv', 'xlsx', 'sqlite']), default='json')
@click.option('--input-file', type=click.Path(exists=True), help='Batch input file (CSV/TXT)')
@click.option('--output-path', type=click.Path(), default='./output', help='Output directory')
@click.option('--include-timestamp', is_flag=True, help='Include timestamp in output filename')
@click.pass_context
def batch(ctx, format, input_file, output_path, include_timestamp):
    """Process batch requests from input file."""
    from src.batch_processor import BatchProcessor

    processor = BatchProcessor(
        config=ctx.obj['config'],
        output_format=format,
        output_path=output_path,
        include_timestamp=include_timestamp,
        timestamp_format=ctx.obj['config'].get('timestamp_format', '%Y%m%d_%H%M%S'),
    )
    processor.process_file(input_file)


if __name__ == '__main__':
    cli(obj={})
