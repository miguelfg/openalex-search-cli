"""
CLI commands for autocomplete resource.
"""

import click

from src.client import APIClient


@click.group()
@click.pass_context
def autocomplete_group(ctx):
    """Manage Autocomplete resources."""
    ctx.obj = ctx.obj or {}


@autocomplete_group.command()
@click.option("--format", type=click.Choice(["json", "csv", "xlsx"]), default="json")
@click.pass_context
def list(ctx, format):
    """List all autocomplete."""
    client = APIClient(ctx.obj["config"])
    try:
        results = client.get("/autocomplete/{entity_type}")
        if format == "json":
            import json

            click.echo(json.dumps(results, indent=2))
        else:
            click.echo(f"Format {format} not yet implemented")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@autocomplete_group.command()
@click.argument("id")
@click.pass_context
def get(ctx, id):
    """Get a autocomplet by ID."""
    client = APIClient(ctx.obj["config"])
    try:
        result = client.get("/autocomplete/{entity_type}/{id}")
        import json

        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
