"""
Shared Click helpers for OpenAlex resource commands.
"""

import json
from typing import Any, Callable
from urllib.parse import quote

import click

from src.client import APIClient


def echo_json(payload: Any) -> None:
    """Print JSON consistently across commands."""
    click.echo(json.dumps(payload, indent=2))


def build_query_params(**values: Any) -> dict[str, Any]:
    """Return only query params explicitly provided by the user."""
    return {key: value for key, value in values.items() if value is not None}


def normalize_sort(sort: str | None) -> str | None:
    """Accept OpenAlex docs shorthand like -cited_by_count."""
    if sort is None:
        return None
    if sort.startswith("-") and len(sort) > 1:
        return f"{sort[1:]}:desc"
    if sort.startswith("+") and len(sort) > 1:
        return f"{sort[1:]}:asc"
    return sort


def quote_path_segment(value: str) -> str:
    """Quote user-provided path segments while preserving OpenAlex prefixes."""
    return quote(value, safe=":")


def add_common_list_options(func: Callable) -> Callable:
    """Attach common OpenAlex list query options to a Click command."""
    options = [
        click.option("--seed", type=int, help="Seed for reproducible random samples."),
        click.option("--select", help="Comma-separated fields to return."),
        click.option(
            "--sample",
            type=click.IntRange(min=1, max=10000),
            help="Return a random sample of N results.",
        ),
        click.option("--cursor", help="Cursor for deep pagination. Use '*' to start."),
        click.option(
            "--page", type=click.IntRange(min=1), help="Page number for pagination."
        ),
        click.option(
            "--per-page",
            type=click.IntRange(min=1, max=100),
            help="Results per page, 1-100.",
        ),
        click.option("--group-by", "group_by", help="Group results by a field."),
        click.option(
            "--sort", help="Sort field. Prefix with '-' for descending order."
        ),
        click.option("--search", help="Full-text search query."),
        click.option(
            "--filter",
            "filter_",
            help="OpenAlex filter expression, e.g. publication_year:2024.",
        ),
        click.option(
            "--format",
            "output_format",
            type=click.Choice(["json"]),
            default="json",
            show_default=True,
        ),
    ]
    for option in options:
        func = option(func)
    return func


def standard_resource_group(
    command_name: str, endpoint: str, include_get: bool = True
) -> click.Group:
    """Build a Click group for an OpenAlex resource with standard list/get commands."""

    @click.group(name=command_name)
    @click.pass_context
    def group(ctx: click.Context) -> None:
        """Query an OpenAlex resource."""
        ctx.obj = ctx.obj or {}

    @group.command(name="list")
    @add_common_list_options
    @click.pass_context
    def list_command(
        ctx: click.Context,
        output_format: str,
        filter_: str | None,
        search: str | None,
        sort: str | None,
        group_by: str | None,
        per_page: int | None,
        page: int | None,
        cursor: str | None,
        sample: int | None,
        select: str | None,
        seed: int | None,
    ) -> None:
        """List records."""
        del output_format
        params = build_query_params(
            filter=filter_,
            search=search,
            sort=normalize_sort(sort),
            group_by=group_by,
            per_page=per_page,
            page=page,
            cursor=cursor,
            sample=sample,
            select=select,
            seed=seed,
        )
        client = APIClient(ctx.obj["config"])
        try:
            echo_json(client.get(endpoint, params=params))
        except Exception as exc:
            raise click.ClickException(str(exc)) from None

    if include_get:

        @group.command(name="get")
        @click.argument("id")
        @click.option("--select", help="Comma-separated fields to return.")
        @click.pass_context
        def get_command(ctx: click.Context, id: str, select: str | None) -> None:
            """Get one record by OpenAlex ID."""
            params = build_query_params(select=select)
            client = APIClient(ctx.obj["config"])
            try:
                echo_json(
                    client.get(f"{endpoint}/{quote_path_segment(id)}", params=params)
                )
            except Exception as exc:
                raise click.ClickException(str(exc)) from None

    return group
