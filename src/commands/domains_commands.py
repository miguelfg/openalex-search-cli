"""
CLI commands for domains resource.
"""

import click
from src.client import APIClient


@click.group()
@click.pass_context
def domains_group(ctx):
    """Manage Domains resources."""
    ctx.obj = ctx.obj or {}


@domains_group.command()
@click.option('--format', type=click.Choice(['json', 'csv', 'xlsx']), default='json')
@click.pass_context
def list(ctx, format):
    """List all domains."""
    client = APIClient(ctx.obj['config'])
    try:
        results = client.get('/domains')
        if format == 'json':
            import json
            click.echo(json.dumps(results, indent=2))
        else:
            click.echo(f"Format {format} not yet implemented")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@domains_group.command()
@click.argument('id')
@click.pass_context
def get(ctx, id):
    """Get a domain by ID."""
    client = APIClient(ctx.obj['config'])
    try:
        result = client.get(f'/domains/{id}')
        import json
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@domains_group.command()
@click.option('--data', type=str, help='JSON data for the domain')
@click.pass_context
def create(ctx, data):
    """Create a new domain."""
    client = APIClient(ctx.obj['config'])
    try:
        import json
        payload = json.loads(data) if data else {}
        result = client.post('/domains', payload)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
