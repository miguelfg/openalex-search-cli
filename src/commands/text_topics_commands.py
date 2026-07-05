"""
CLI commands for text_topics resource.
"""

import click
from src.client import APIClient


@click.group()
@click.pass_context
def text_topics_group(ctx):
    """Manage Text_topics resources."""
    ctx.obj = ctx.obj or {}


@text_topics_group.command()
@click.option('--format', type=click.Choice(['json', 'csv', 'xlsx']), default='json')
@click.pass_context
def list(ctx, format):
    """List all text_topics."""
    client = APIClient(ctx.obj['config'])
    try:
        results = client.get('/text_topics')
        if format == 'json':
            import json
            click.echo(json.dumps(results, indent=2))
        else:
            click.echo(f"Format {format} not yet implemented")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@text_topics_group.command()
@click.argument('id')
@click.pass_context
def get(ctx, id):
    """Get a text_topic by ID."""
    client = APIClient(ctx.obj['config'])
    try:
        result = client.get(f'/text_topics/{id}')
        import json
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@text_topics_group.command()
@click.option('--data', type=str, help='JSON data for the text_topic')
@click.pass_context
def create(ctx, data):
    """Create a new text_topic."""
    client = APIClient(ctx.obj['config'])
    try:
        import json
        payload = json.loads(data) if data else {}
        result = client.post('/text_topics', payload)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
