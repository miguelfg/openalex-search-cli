"""
CLI commands for countries resource.
"""

import click
from src.client import APIClient


@click.group()
@click.pass_context
def countries_group(ctx):
    """Manage Countries resources."""
    ctx.obj = ctx.obj or {}


@countries_group.command()
@click.option('--format', type=click.Choice(['json', 'csv', 'xlsx']), default='json')
@click.pass_context
def list(ctx, format):
    """List all countries."""
    client = APIClient(ctx.obj['config'])
    try:
        results = client.get('/countries')
        if format == 'json':
            import json
            click.echo(json.dumps(results, indent=2))
        else:
            click.echo(f"Format {format} not yet implemented")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@countries_group.command()
@click.argument('id')
@click.pass_context
def get(ctx, id):
    """Get a countrie by ID."""
    client = APIClient(ctx.obj['config'])
    try:
        result = client.get('/countries/{id}')
        import json
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@countries_group.command()
@click.option('--data', type=str, help='JSON data for the countrie')
@click.pass_context
def create(ctx, data):
    """Create a new countrie."""
    client = APIClient(ctx.obj['config'])
    try:
        import json
        payload = json.loads(data) if data else {}
        result = client.post('/countries', payload)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
