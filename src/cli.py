#!/usr/bin/env python3
"""
openalex_search_cli - Click CLI for the OpenAlex API.
"""

import click

from src.client import APIClient
from src.commands.common import (
    build_query_params,
    echo_json,
    quote_path_segment,
    standard_resource_group,
)
from src.config import Config

STANDARD_RESOURCES = {
    "works": "/works",
    "authors": "/authors",
    "sources": "/sources",
    "institutions": "/institutions",
    "topics": "/topics",
    "keywords": "/keywords",
    "publishers": "/publishers",
    "funders": "/funders",
    "domains": "/domains",
    "fields": "/fields",
    "subfields": "/subfields",
    "sdgs": "/sdgs",
    "countries": "/countries",
    "continents": "/continents",
    "languages": "/languages",
    "awards": "/awards",
}


@click.group()
@click.option("--config", type=click.Path(exists=False), help="Config file path")
@click.option("--verbose", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx: click.Context, config: str | None, verbose: bool) -> None:
    """
    OpenAlex Search CLI - API client.
    """
    ctx.ensure_object(dict)
    ctx.obj["config"] = Config(config_path=config)
    ctx.obj["verbose"] = verbose


@click.group()
@click.pass_context
def autocomplete_group(ctx: click.Context) -> None:
    """Search OpenAlex autocomplete endpoints."""
    ctx.obj = ctx.obj or {}


@autocomplete_group.command(name="search")
@click.argument("entity_type")
@click.option("--q", required=True, help="Autocomplete query.")
@click.option("--filter", "filter_", help="Optional OpenAlex filter expression.")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json"]),
    default="json",
    show_default=True,
)
@click.pass_context
def autocomplete_search(
    ctx: click.Context,
    entity_type: str,
    q: str,
    filter_: str | None,
    output_format: str,
) -> None:
    """Autocomplete an entity type, such as works, authors, or institutions."""
    del output_format
    client = APIClient(ctx.obj["config"])
    params = build_query_params(q=q, filter=filter_)
    try:
        echo_json(
            client.get(
                f"/autocomplete/{quote_path_segment(entity_type)}", params=params
            )
        )
    except Exception as exc:
        raise click.ClickException(str(exc)) from None


@click.group(name="changefiles")
@click.pass_context
def changefiles_group(ctx: click.Context) -> None:
    """Query OpenAlex changefiles."""
    ctx.obj = ctx.obj or {}


@changefiles_group.command(name="list")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json"]),
    default="json",
    show_default=True,
)
@click.pass_context
def changefiles_list(ctx: click.Context, output_format: str) -> None:
    """List available changefiles."""
    del output_format
    client = APIClient(ctx.obj["config"])
    try:
        echo_json(client.get("/changefiles"))
    except Exception as exc:
        raise click.ClickException(str(exc)) from None


@changefiles_group.command(name="get")
@click.argument("date")
@click.pass_context
def changefiles_get(ctx: click.Context, date: str) -> None:
    """Get changefiles for a date, formatted as YYYY-MM-DD."""
    client = APIClient(ctx.obj["config"])
    try:
        echo_json(client.get(f"/changefiles/{quote_path_segment(date)}"))
    except Exception as exc:
        raise click.ClickException(str(exc)) from None


@click.group(name="rate_limit")
@click.pass_context
def rate_limit_group(ctx: click.Context) -> None:
    """Check the authenticated OpenAlex rate-limit status."""
    ctx.obj = ctx.obj or {}


@rate_limit_group.command(name="get")
@click.pass_context
def rate_limit_get(ctx: click.Context) -> None:
    """Get rate-limit status. Requires a valid API key."""
    client = APIClient(ctx.obj["config"])
    try:
        echo_json(client.get("/rate-limit"))
    except Exception as exc:
        raise click.ClickException(str(exc)) from None


@rate_limit_group.command(name="list")
@click.pass_context
def rate_limit_list(ctx: click.Context) -> None:
    """Alias for rate_limit get."""
    client = APIClient(ctx.obj["config"])
    try:
        echo_json(client.get("/rate-limit"))
    except Exception as exc:
        raise click.ClickException(str(exc)) from None


@click.group(name="text_topics")
@click.pass_context
def text_topics_group(ctx: click.Context) -> None:
    """Classify text with OpenAlex text topics."""
    ctx.obj = ctx.obj or {}


@text_topics_group.command(name="classify")
@click.option("--title", help="Title text to classify.")
@click.option("--abstract", help="Abstract text to classify.")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json"]),
    default="json",
    show_default=True,
)
@click.pass_context
def text_topics_classify(
    ctx: click.Context,
    title: str | None,
    abstract: str | None,
    output_format: str,
) -> None:
    """Classify a title and/or abstract into OpenAlex topics."""
    del output_format
    client = APIClient(ctx.obj["config"])
    params = build_query_params(title=title, abstract=abstract)
    try:
        echo_json(client.get("/text/topics", params=params))
    except Exception as exc:
        raise click.ClickException(str(exc)) from None


for command_name, endpoint in STANDARD_RESOURCES.items():
    cli.add_command(standard_resource_group(command_name, endpoint), command_name)

cli.add_command(autocomplete_group, "autocomplete")
cli.add_command(changefiles_group, "changefiles")
cli.add_command(rate_limit_group, "rate_limit")
cli.add_command(text_topics_group, "text_topics")


@cli.command()
@click.option(
    "--format", type=click.Choice(["json", "csv", "xlsx", "sqlite"]), default="json"
)
@click.option(
    "--input-file", type=click.Path(exists=True), help="Batch input file (CSV/TXT)"
)
@click.option(
    "--output-path", type=click.Path(), default="./output", help="Output directory"
)
@click.option(
    "--include-timestamp", is_flag=True, help="Include timestamp in output filename"
)
@click.pass_context
def batch(
    ctx: click.Context,
    format: str,
    input_file: str,
    output_path: str,
    include_timestamp: bool,
) -> None:
    """Process batch requests from input file."""
    from src.batch_processor import BatchProcessor

    processor = BatchProcessor(
        config=ctx.obj["config"],
        output_format=format,
        output_path=output_path,
        include_timestamp=include_timestamp,
        timestamp_format=ctx.obj["config"].get("timestamp_format", "%Y%m%d_%H%M%S"),
    )
    processor.process_file(input_file)


if __name__ == "__main__":
    cli(obj={})
