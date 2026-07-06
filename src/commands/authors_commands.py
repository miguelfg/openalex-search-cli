"""
CLI commands for authors resource.
"""

import click

from src.client import APIClient


@click.group()
@click.pass_context
def authors_group(ctx):
    """Manage Authors resources."""
    ctx.obj = ctx.obj or {}


@authors_group.command()
@click.option("--format", type=click.Choice(["json", "csv", "xlsx"]), default="json")
@click.pass_context
def list(ctx, format):
    """List all authors."""
    client = APIClient(ctx.obj["config"])
    try:
        results = client.get("/authors")
        if format == "json":
            import json

            click.echo(json.dumps(results, indent=2))
        else:
            click.echo(f"Format {format} not yet implemented")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@authors_group.command()
@click.argument("id")
@click.pass_context
def get(ctx, id):
    """Get a author by ID."""
    client = APIClient(ctx.obj["config"])
    try:
        result = client.get(f"/authors/{id}")
        import json

        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
