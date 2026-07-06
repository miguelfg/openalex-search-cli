"""
CLI commands for keywords resource.
"""

import click

from src.client import APIClient


@click.group()
@click.pass_context
def keywords_group(ctx):
    """Manage Keywords resources."""
    ctx.obj = ctx.obj or {}


@keywords_group.command()
@click.option("--format", type=click.Choice(["json", "csv", "xlsx"]), default="json")
@click.pass_context
def list(ctx, format):
    """List all keywords."""
    client = APIClient(ctx.obj["config"])
    try:
        results = client.get("/keywords")
        if format == "json":
            import json

            click.echo(json.dumps(results, indent=2))
        else:
            click.echo(f"Format {format} not yet implemented")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@keywords_group.command()
@click.argument("id")
@click.pass_context
def get(ctx, id):
    """Get a keyword by ID."""
    client = APIClient(ctx.obj["config"])
    try:
        result = client.get(f"/keywords/{id}")
        import json

        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
