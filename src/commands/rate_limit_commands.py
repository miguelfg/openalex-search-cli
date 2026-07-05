"""
CLI commands for rate_limit resource.
"""

import click
from src.client import APIClient


@click.group()
@click.pass_context
def rate_limit_group(ctx):
    """Manage Rate_limit resources."""
    ctx.obj = ctx.obj or {}


@rate_limit_group.command()
@click.option('--format', type=click.Choice(['json', 'csv', 'xlsx']), default='json')
@click.pass_context
def list(ctx, format):
    """List all rate_limit."""
    client = APIClient(ctx.obj['config'])
    try:
        results = client.get('/rate-limit')
        if format == 'json':
            import json
            click.echo(json.dumps(results, indent=2))
        else:
            click.echo(f"Format {format} not yet implemented")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@rate_limit_group.command()
@click.argument('id')
@click.pass_context
def get(ctx, id):
    """Get a rate_limi by ID."""
    client = APIClient(ctx.obj['config'])
    try:
        result = client.get('/rate-limit/{id}')
        import json
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
