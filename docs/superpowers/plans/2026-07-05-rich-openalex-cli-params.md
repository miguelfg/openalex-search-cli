# Rich OpenAlex CLI Params Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enrich the generated OpenAlex CLI so resource commands expose the useful query parameters documented in `docs/openalex-api.yaml`.

**Architecture:** Add shared command-building utilities that centralize list/get options and JSON output. Rewire `src/cli.py` to register standard resource groups from a single module, then add special command groups for autocomplete, text classification, rate limits, and changefiles. Keep `src.client.APIClient` authentication and endpoint validation behavior unchanged.

**Tech Stack:** Python 3.10+, Click, requests, pytest, uv, OpenAlex OpenAPI spec in `docs/openalex-api.yaml`.

---

## Scope Check

This is one coherent CLI enrichment project. It includes standard resource list/get behavior, special endpoints, missing endpoints, tests, and docs. It does not implement per-command CSV/XLSX export, because the project docs say per-resource commands intentionally only support JSON while batch owns multi-format export.

## File Structure

- Create `src/commands/common.py`: shared Click option decorators, query param builder, JSON output, endpoint path helpers, and a standard resource group factory.
- Modify existing generated command modules: replace repetitive list/get implementations with calls to the shared standard resource group factory.
- Modify `src/cli.py`: import and register the missing resource command groups.
- Modify `tests/test_cli.py`: add behavioral tests for rich params, special endpoints, missing commands, endpoint safety, and no API key leakage regression.
- Modify `README.md`: document representative rich CLI usage.
- Keep the existing module-per-resource layout so imports using `src.commands.<resource>_commands` remain stable.

## Standard Resource Coverage

These standard resources get `list` and `get`:

- `works` -> `/works`, `/works/{id}`
- `authors` -> `/authors`, `/authors/{id}`
- `sources` -> `/sources`, `/sources/{id}`
- `institutions` -> `/institutions`, `/institutions/{id}`
- `topics` -> `/topics`, `/topics/{id}`
- `keywords` -> `/keywords`, `/keywords/{id}`
- `publishers` -> `/publishers`, `/publishers/{id}`
- `funders` -> `/funders`, `/funders/{id}`
- `domains` -> `/domains`, `/domains/{id}`
- `fields` -> `/fields`, `/fields/{id}`
- `subfields` -> `/subfields`, `/subfields/{id}`
- `sdgs` -> `/sdgs`, `/sdgs/{id}`
- `countries` -> `/countries`, `/countries/{id}`
- `continents` -> `/continents`, `/continents/{id}`
- `languages` -> `/languages`, `/languages/{id}`
- `awards` -> `/awards`, `/awards/{id}`
- `concepts` -> `/concepts`, `/concepts/{id}`

These list-only resources get `list`:

- `work-types` -> `/work-types`
- `source-types` -> `/source-types`
- `institution-types` -> `/institution-types`
- `licenses` -> `/licenses`

Every standard `list` gets:

```text
--filter
--search
--sort
--group-by
--per-page
--page
--cursor
--sample
--select
--format json
```

Every standard `get` gets:

```text
ID
--select
```

## Special Endpoint Coverage

- `autocomplete search ENTITY_TYPE --q QUERY [--filter FILTER]`
- `text_topics classify [--title TITLE] [--abstract ABSTRACT]`
- `rate_limit get`
- `changefiles list`
- `changefiles get DATE`

---

### Task 1: Tests for Query Param Plumbing

**Files:**
- Modify: `tests/test_cli.py`
- Create: `src/commands/common.py`

- [ ] **Step 1: Write failing tests for common query params**

Append this code to `tests/test_cli.py`:

```python

def test_works_list_passes_common_query_params(monkeypatch):
    calls = []

    def fake_get(self, endpoint, params=None):
        calls.append((endpoint, params))
        return {"results": [{"id": "W1"}]}

    monkeypatch.setattr("src.client.APIClient.get", fake_get)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "works",
            "list",
            "--filter",
            "publication_year:2024",
            "--search",
            "machine learning",
            "--sort",
            "-cited_by_count",
            "--group-by",
            "publication_year",
            "--per-page",
            "50",
            "--page",
            "2",
            "--cursor",
            "*",
            "--sample",
            "10",
            "--select",
            "id,display_name",
        ],
    )

    assert result.exit_code == 0
    assert calls == [
        (
            "/works",
            {
                "filter": "publication_year:2024",
                "search": "machine learning",
                "sort": "-cited_by_count",
                "group_by": "publication_year",
                "per_page": 50,
                "page": 2,
                "cursor": "*",
                "sample": 10,
                "select": "id,display_name",
            },
        )
    ]
    assert '"W1"' in result.output


def test_works_get_passes_select(monkeypatch):
    calls = []

    def fake_get(self, endpoint, params=None):
        calls.append((endpoint, params))
        return {"id": "W2741809807", "display_name": "Example"}

    monkeypatch.setattr("src.client.APIClient.get", fake_get)

    runner = CliRunner()
    result = runner.invoke(cli, ["works", "get", "W2741809807", "--select", "id,display_name"])

    assert result.exit_code == 0
    assert calls == [("/works/W2741809807", {"select": "id,display_name"})]
    assert "Example" in result.output
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/test_cli.py::test_works_list_passes_common_query_params tests/test_cli.py::test_works_get_passes_select -v
```

Expected: both tests fail because `works list` does not recognize the new options and `works get` does not recognize `--select`.

- [ ] **Step 3: Create shared command helpers**

Create `src/commands/common.py` with this complete content:

```python
"""
Shared Click command helpers for OpenAlex resources.
"""

import json
from functools import wraps
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


def add_common_list_options(func: Callable) -> Callable:
    """Attach OpenAlex list query options to a Click command."""
    options = [
        click.option("--select", help="Comma-separated fields to return."),
        click.option("--sample", type=click.IntRange(min=1, max=10000), help="Return a random sample of N results."),
        click.option("--cursor", help="Cursor for deep pagination. Use '*' to start."),
        click.option("--page", type=click.IntRange(min=1), help="Page number for pagination."),
        click.option("--per-page", type=click.IntRange(min=1, max=100), help="Results per page, 1-100."),
        click.option("--group-by", "group_by", help="Group results by a field."),
        click.option("--sort", help="Sort field. Prefix with '-' for descending order."),
        click.option("--search", help="Full-text search query."),
        click.option("--filter", "filter_", help="OpenAlex filter expression, e.g. publication_year:2024."),
        click.option("--format", "output_format", type=click.Choice(["json"]), default="json", show_default=True),
    ]
    for option in options:
        func = option(func)
    return func


def add_select_option(func: Callable) -> Callable:
    """Attach the OpenAlex select query option to a single-record command."""
    return click.option("--select", help="Comma-separated fields to return.")(func)


def quote_path_segment(value: str) -> str:
    """Quote user-provided path segments while preserving external-ID prefixes."""
    return quote(value, safe=":")


def standard_resource_group(command_name: str, label: str, endpoint: str, include_get: bool = True) -> click.Group:
    """Build a Click group for an OpenAlex resource with standard list/get commands."""

    @click.group(name=command_name)
    @click.pass_context
    def group(ctx: click.Context) -> None:
        """Manage an OpenAlex resource."""
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
    ) -> None:
        """List OpenAlex records."""
        client = APIClient(ctx.obj["config"])
        params = build_query_params(
            filter=filter_,
            search=search,
            sort=sort,
            group_by=group_by,
            per_page=per_page,
            page=page,
            cursor=cursor,
            sample=sample,
            select=select,
        )
        echo_json(client.get(endpoint, params=params))

    if include_get:

        @group.command(name="get")
        @click.argument("id")
        @add_select_option
        @click.pass_context
        def get_command(ctx: click.Context, id: str, select: str | None) -> None:
            """Get one OpenAlex record by ID or supported external ID."""
            client = APIClient(ctx.obj["config"])
            params = build_query_params(select=select)
            echo_json(client.get(f"{endpoint}/{quote_path_segment(id)}", params=params))

    group.help = f"Manage {label} resources."
    return group
```

- [ ] **Step 4: Rewire `works` through the helper**

Replace `src/commands/works_commands.py` with this complete content:

```python
"""
CLI commands for works resource.
"""

from src.commands.common import standard_resource_group


works_group = standard_resource_group("works", "Works", "/works")
```

- [ ] **Step 5: Run tests to verify the first resource passes**

Run:

```bash
uv run pytest tests/test_cli.py::test_works_list_passes_common_query_params tests/test_cli.py::test_works_get_passes_select -v
```

Expected: both tests pass.

- [ ] **Step 6: Commit**

Run:

```bash
git add src/commands/common.py src/commands/works_commands.py tests/test_cli.py
git commit -m "feat: add rich params for works commands"
```

Expected: commit succeeds.

---

### Task 2: Rewire Standard Existing Resources

**Files:**
- Modify: `src/commands/authors_commands.py`
- Modify: `src/commands/sources_commands.py`
- Modify: `src/commands/institutions_commands.py`
- Modify: `src/commands/topics_commands.py`
- Modify: `src/commands/keywords_commands.py`
- Modify: `src/commands/publishers_commands.py`
- Modify: `src/commands/funders_commands.py`
- Modify: `src/commands/domains_commands.py`
- Modify: `src/commands/fields_commands.py`
- Modify: `src/commands/subfields_commands.py`
- Modify: `src/commands/sdgs_commands.py`
- Modify: `src/commands/countries_commands.py`
- Modify: `src/commands/continents_commands.py`
- Modify: `src/commands/languages_commands.py`
- Modify: `src/commands/awards_commands.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write failing tests for another resource**

Append this code to `tests/test_cli.py`:

```python

def test_authors_list_passes_common_query_params(monkeypatch):
    calls = []

    def fake_get(self, endpoint, params=None):
        calls.append((endpoint, params))
        return {"results": [{"id": "A5023888391"}]}

    monkeypatch.setattr("src.client.APIClient.get", fake_get)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "authors",
            "list",
            "--filter",
            "has_orcid:true",
            "--search",
            "Ada Lovelace",
            "--sort",
            "-works_count",
            "--per-page",
            "5",
            "--select",
            "id,display_name",
        ],
    )

    assert result.exit_code == 0
    assert calls == [
        (
            "/authors",
            {
                "filter": "has_orcid:true",
                "search": "Ada Lovelace",
                "sort": "-works_count",
                "per_page": 5,
                "select": "id,display_name",
            },
        )
    ]
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
uv run pytest tests/test_cli.py::test_authors_list_passes_common_query_params -v
```

Expected: test fails because `authors list` does not recognize the new options.

- [ ] **Step 3: Replace each existing standard module**

Use these exact file contents:

`src/commands/authors_commands.py`

```python
"""
CLI commands for authors resource.
"""

from src.commands.common import standard_resource_group


authors_group = standard_resource_group("authors", "Authors", "/authors")
```

`src/commands/sources_commands.py`

```python
"""
CLI commands for sources resource.
"""

from src.commands.common import standard_resource_group


sources_group = standard_resource_group("sources", "Sources", "/sources")
```

`src/commands/institutions_commands.py`

```python
"""
CLI commands for institutions resource.
"""

from src.commands.common import standard_resource_group


institutions_group = standard_resource_group("institutions", "Institutions", "/institutions")
```

`src/commands/topics_commands.py`

```python
"""
CLI commands for topics resource.
"""

from src.commands.common import standard_resource_group


topics_group = standard_resource_group("topics", "Topics", "/topics")
```

`src/commands/keywords_commands.py`

```python
"""
CLI commands for keywords resource.
"""

from src.commands.common import standard_resource_group


keywords_group = standard_resource_group("keywords", "Keywords", "/keywords")
```

`src/commands/publishers_commands.py`

```python
"""
CLI commands for publishers resource.
"""

from src.commands.common import standard_resource_group


publishers_group = standard_resource_group("publishers", "Publishers", "/publishers")
```

`src/commands/funders_commands.py`

```python
"""
CLI commands for funders resource.
"""

from src.commands.common import standard_resource_group


funders_group = standard_resource_group("funders", "Funders", "/funders")
```

`src/commands/domains_commands.py`

```python
"""
CLI commands for domains resource.
"""

from src.commands.common import standard_resource_group


domains_group = standard_resource_group("domains", "Domains", "/domains")
```

`src/commands/fields_commands.py`

```python
"""
CLI commands for fields resource.
"""

from src.commands.common import standard_resource_group


fields_group = standard_resource_group("fields", "Fields", "/fields")
```

`src/commands/subfields_commands.py`

```python
"""
CLI commands for subfields resource.
"""

from src.commands.common import standard_resource_group


subfields_group = standard_resource_group("subfields", "Subfields", "/subfields")
```

`src/commands/sdgs_commands.py`

```python
"""
CLI commands for sdgs resource.
"""

from src.commands.common import standard_resource_group


sdgs_group = standard_resource_group("sdgs", "SDGs", "/sdgs")
```

`src/commands/countries_commands.py`

```python
"""
CLI commands for countries resource.
"""

from src.commands.common import standard_resource_group


countries_group = standard_resource_group("countries", "Countries", "/countries")
```

`src/commands/continents_commands.py`

```python
"""
CLI commands for continents resource.
"""

from src.commands.common import standard_resource_group


continents_group = standard_resource_group("continents", "Continents", "/continents")
```

`src/commands/languages_commands.py`

```python
"""
CLI commands for languages resource.
"""

from src.commands.common import standard_resource_group


languages_group = standard_resource_group("languages", "Languages", "/languages")
```

`src/commands/awards_commands.py`

```python
"""
CLI commands for awards resource.
"""

from src.commands.common import standard_resource_group


awards_group = standard_resource_group("awards", "Awards", "/awards")
```

- [ ] **Step 4: Run focused tests**

Run:

```bash
uv run pytest tests/test_cli.py::test_works_list_passes_common_query_params tests/test_cli.py::test_works_get_passes_select tests/test_cli.py::test_authors_list_passes_common_query_params -v
```

Expected: all three tests pass.

- [ ] **Step 5: Run smoke help for a rewritten module**

Run:

```bash
uv run openalex-search-cli sources list --help
```

Expected: output includes `--filter`, `--search`, `--sort`, `--group-by`, `--per-page`, `--page`, `--cursor`, `--sample`, and `--select`.

- [ ] **Step 6: Commit**

Run:

```bash
git add src/commands/*_commands.py tests/test_cli.py
git commit -m "feat: add rich params to standard resources"
```

Expected: commit succeeds.

---

### Task 3: Fix Special Endpoint Commands

**Files:**
- Modify: `src/commands/autocomplete_commands.py`
- Modify: `src/commands/text_topics_commands.py`
- Modify: `src/commands/rate_limit_commands.py`
- Modify: `src/commands/changefiles_commands.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write failing tests for special endpoints**

Append this code to `tests/test_cli.py`:

```python

def test_autocomplete_search_uses_entity_type_and_query(monkeypatch):
    calls = []

    def fake_get(self, endpoint, params=None):
        calls.append((endpoint, params))
        return {"results": [{"id": "W1", "display_name": "Machine learning"}]}

    monkeypatch.setattr("src.client.APIClient.get", fake_get)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["autocomplete", "search", "works", "--q", "machine", "--filter", "publication_year:2024"],
    )

    assert result.exit_code == 0
    assert calls == [("/autocomplete/works", {"q": "machine", "filter": "publication_year:2024"})]


def test_text_topics_classify_uses_spec_path(monkeypatch):
    calls = []

    def fake_get(self, endpoint, params=None):
        calls.append((endpoint, params))
        return {"topics": []}

    monkeypatch.setattr("src.client.APIClient.get", fake_get)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["text_topics", "classify", "--title", "A title", "--abstract", "An abstract"],
    )

    assert result.exit_code == 0
    assert calls == [("/text/topics", {"title": "A title", "abstract": "An abstract"})]


def test_rate_limit_get_uses_spec_path(monkeypatch):
    calls = []

    def fake_get(self, endpoint, params=None):
        calls.append((endpoint, params))
        return {"remaining": 100}

    monkeypatch.setattr("src.client.APIClient.get", fake_get)

    runner = CliRunner()
    result = runner.invoke(cli, ["rate_limit", "get"])

    assert result.exit_code == 0
    assert calls == [("/rate-limit", None)]
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/test_cli.py::test_autocomplete_search_uses_entity_type_and_query tests/test_cli.py::test_text_topics_classify_uses_spec_path tests/test_cli.py::test_rate_limit_get_uses_spec_path -v
```

Expected: tests fail because current generated commands expose wrong command names or wrong paths.

- [ ] **Step 3: Replace autocomplete command**

Replace `src/commands/autocomplete_commands.py` with this complete content:

```python
"""
CLI commands for the OpenAlex autocomplete endpoint.
"""

import click

from src.client import APIClient
from src.commands.common import build_query_params, echo_json, quote_path_segment


ENTITY_TYPES = ["works", "authors", "sources", "institutions", "topics", "keywords", "publishers", "funders"]


@click.group()
@click.pass_context
def autocomplete_group(ctx: click.Context) -> None:
    """Search OpenAlex entity names with autocomplete."""
    ctx.obj = ctx.obj or {}


@autocomplete_group.command(name="search")
@click.argument("entity_type", type=click.Choice(ENTITY_TYPES))
@click.option("--q", required=True, help="Search query string.")
@click.option("--filter", "filter_", help="OpenAlex filter expression.")
@click.pass_context
def search_command(ctx: click.Context, entity_type: str, q: str, filter_: str | None) -> None:
    """Run autocomplete for an entity type."""
    client = APIClient(ctx.obj["config"])
    params = build_query_params(q=q, filter=filter_)
    echo_json(client.get(f"/autocomplete/{quote_path_segment(entity_type)}", params=params))
```

- [ ] **Step 4: Replace text topics command**

Replace `src/commands/text_topics_commands.py` with this complete content:

```python
"""
CLI commands for the deprecated OpenAlex text topics endpoint.
"""

import click

from src.client import APIClient
from src.commands.common import build_query_params, echo_json


@click.group()
@click.pass_context
def text_topics_group(ctx: click.Context) -> None:
    """Classify text into OpenAlex topics."""
    ctx.obj = ctx.obj or {}


@text_topics_group.command(name="classify")
@click.option("--title", help="Title text to classify.")
@click.option("--abstract", help="Abstract text to classify.")
@click.pass_context
def classify_command(ctx: click.Context, title: str | None, abstract: str | None) -> None:
    """Classify title and abstract text."""
    client = APIClient(ctx.obj["config"])
    params = build_query_params(title=title, abstract=abstract)
    echo_json(client.get("/text/topics", params=params))
```

- [ ] **Step 5: Replace rate limit command**

Replace `src/commands/rate_limit_commands.py` with this complete content:

```python
"""
CLI commands for the OpenAlex rate limit endpoint.
"""

import click

from src.client import APIClient
from src.commands.common import echo_json


@click.group()
@click.pass_context
def rate_limit_group(ctx: click.Context) -> None:
    """Check OpenAlex rate limit status."""
    ctx.obj = ctx.obj or {}


@rate_limit_group.command(name="get")
@click.pass_context
def get_command(ctx: click.Context) -> None:
    """Get current rate limit status."""
    client = APIClient(ctx.obj["config"])
    echo_json(client.get("/rate-limit"))
```

- [ ] **Step 6: Replace changefiles command**

Replace `src/commands/changefiles_commands.py` with this complete content:

```python
"""
CLI commands for OpenAlex changefiles.
"""

import click

from src.client import APIClient
from src.commands.common import echo_json, quote_path_segment


@click.group()
@click.pass_context
def changefiles_group(ctx: click.Context) -> None:
    """List and fetch OpenAlex changefiles."""
    ctx.obj = ctx.obj or {}


@changefiles_group.command(name="list")
@click.pass_context
def list_command(ctx: click.Context) -> None:
    """List available changefile dates."""
    client = APIClient(ctx.obj["config"])
    echo_json(client.get("/changefiles"))


@changefiles_group.command(name="get")
@click.argument("date")
@click.pass_context
def get_command(ctx: click.Context, date: str) -> None:
    """Get changefile details for a date in YYYY-MM-DD format."""
    client = APIClient(ctx.obj["config"])
    echo_json(client.get(f"/changefiles/{quote_path_segment(date)}"))
```

- [ ] **Step 7: Run special endpoint tests**

Run:

```bash
uv run pytest tests/test_cli.py::test_autocomplete_search_uses_entity_type_and_query tests/test_cli.py::test_text_topics_classify_uses_spec_path tests/test_cli.py::test_rate_limit_get_uses_spec_path -v
```

Expected: all three tests pass.

- [ ] **Step 8: Commit**

Run:

```bash
git add src/commands/autocomplete_commands.py src/commands/text_topics_commands.py src/commands/rate_limit_commands.py src/commands/changefiles_commands.py tests/test_cli.py
git commit -m "fix: align special commands with OpenAlex spec"
```

Expected: commit succeeds.

---

### Task 4: Add Missing Spec Resources

**Files:**
- Create: `src/commands/concepts_commands.py`
- Create: `src/commands/work_types_commands.py`
- Create: `src/commands/source_types_commands.py`
- Create: `src/commands/institution_types_commands.py`
- Create: `src/commands/licenses_commands.py`
- Modify: `src/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write failing tests for missing resources**

Append this code to `tests/test_cli.py`:

```python

def test_missing_spec_resources_are_registered():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "concepts" in result.output
    assert "work-types" in result.output
    assert "source-types" in result.output
    assert "institution-types" in result.output
    assert "licenses" in result.output


def test_work_types_list_uses_spec_path(monkeypatch):
    calls = []

    def fake_get(self, endpoint, params=None):
        calls.append((endpoint, params))
        return {"results": [{"id": "article"}]}

    monkeypatch.setattr("src.client.APIClient.get", fake_get)

    runner = CliRunner()
    result = runner.invoke(cli, ["work-types", "list", "--filter", "id:article"])

    assert result.exit_code == 0
    assert calls == [("/work-types", {"filter": "id:article"})]
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/test_cli.py::test_missing_spec_resources_are_registered tests/test_cli.py::test_work_types_list_uses_spec_path -v
```

Expected: tests fail because the commands are not registered.

- [ ] **Step 3: Add missing command modules**

Create `src/commands/concepts_commands.py`:

```python
"""
CLI commands for deprecated concepts resource.
"""

from src.commands.common import standard_resource_group


concepts_group = standard_resource_group("concepts", "Concepts", "/concepts")
```

Create `src/commands/work_types_commands.py`:

```python
"""
CLI commands for work types resource.
"""

from src.commands.common import standard_resource_group


work_types_group = standard_resource_group("work-types", "Work Types", "/work-types", include_get=False)
```

Create `src/commands/source_types_commands.py`:

```python
"""
CLI commands for source types resource.
"""

from src.commands.common import standard_resource_group


source_types_group = standard_resource_group("source-types", "Source Types", "/source-types", include_get=False)
```

Create `src/commands/institution_types_commands.py`:

```python
"""
CLI commands for institution types resource.
"""

from src.commands.common import standard_resource_group


institution_types_group = standard_resource_group(
    "institution-types",
    "Institution Types",
    "/institution-types",
    include_get=False,
)
```

Create `src/commands/licenses_commands.py`:

```python
"""
CLI commands for licenses resource.
"""

from src.commands.common import standard_resource_group


licenses_group = standard_resource_group("licenses", "Licenses", "/licenses", include_get=False)
```

- [ ] **Step 4: Register missing groups in `src/cli.py`**

Add these imports near the other command imports in `src/cli.py`:

```python
from src.commands.concepts_commands import concepts_group
from src.commands.work_types_commands import work_types_group
from src.commands.source_types_commands import source_types_group
from src.commands.institution_types_commands import institution_types_group
from src.commands.licenses_commands import licenses_group
```

Add these registrations after `text_topics` in `src/cli.py`:

```python
cli.add_command(concepts_group, 'concepts')
cli.add_command(work_types_group, 'work-types')
cli.add_command(source_types_group, 'source-types')
cli.add_command(institution_types_group, 'institution-types')
cli.add_command(licenses_group, 'licenses')
```

- [ ] **Step 5: Run missing resource tests**

Run:

```bash
uv run pytest tests/test_cli.py::test_missing_spec_resources_are_registered tests/test_cli.py::test_work_types_list_uses_spec_path -v
```

Expected: both tests pass.

- [ ] **Step 6: Commit**

Run:

```bash
git add src/cli.py src/commands/concepts_commands.py src/commands/work_types_commands.py src/commands/source_types_commands.py src/commands/institution_types_commands.py src/commands/licenses_commands.py tests/test_cli.py
git commit -m "feat: add missing OpenAlex resource commands"
```

Expected: commit succeeds.

---

### Task 5: Preserve Endpoint Safety and Error Redaction

**Files:**
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write regression tests for quoted IDs and redacted errors**

Append this code to `tests/test_cli.py`:

```python

def test_external_id_path_segments_are_quoted(monkeypatch):
    calls = []

    def fake_get(self, endpoint, params=None):
        calls.append((endpoint, params))
        return {"id": "https://doi.org/10.7717/peerj.4375"}

    monkeypatch.setattr("src.client.APIClient.get", fake_get)

    runner = CliRunner()
    result = runner.invoke(cli, ["works", "get", "https://doi.org/10.7717/peerj.4375"])

    assert result.exit_code == 0
    assert calls == [("/works/https:%2F%2Fdoi.org%2F10.7717%2Fpeerj.4375", {})]


def test_http_error_message_does_not_leak_query_params(monkeypatch):
    import requests
    from src.client import APIClient
    from src.config import Config

    class DummyResponse:
        status_code = 403
        reason = "Forbidden"
        text = '{"error": "forbidden"}'

        def raise_for_status(self):
            raise requests.HTTPError("403 Forbidden for url with api_key=secret")

        def json(self):
            return {"error": "forbidden"}

    def fake_request(self, method, url, params=None, json=None, timeout=None):
        assert params == {"filter": "x:y", "api_key": "secret"}
        return DummyResponse()

    config = Config()
    config.config = {"base_url": "https://api.openalex.org", "api_key": "secret"}
    client = APIClient(config)

    monkeypatch.setattr(client.session, "request", fake_request.__get__(client.session, type(client.session)))

    try:
        client.get("/works", params={"filter": "x:y"})
    except requests.HTTPError as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected requests.HTTPError")

    assert "api_key" not in message
    assert "secret" not in message
    assert message == "403 Forbidden for GET https://api.openalex.org/works"
```

- [ ] **Step 2: Run regression tests**

Run:

```bash
uv run pytest tests/test_cli.py::test_external_id_path_segments_are_quoted tests/test_cli.py::test_http_error_message_does_not_leak_query_params -v
```

Expected: both tests pass. If `test_external_id_path_segments_are_quoted` fails because `params` is `None`, change `standard_resource_group.get_command` to call `client.get(..., params=params or None)` and update the assertion to expect `None`; keep the endpoint assertion unchanged.

- [ ] **Step 3: Run full test suite**

Run:

```bash
make test
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

Run:

```bash
git add tests/test_cli.py
git commit -m "test: cover endpoint safety with rich params"
```

Expected: commit succeeds.

---

### Task 6: Update README Usage

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add rich parameter examples**

Add this section to `README.md` after the basic CLI usage section:

```markdown
## Rich Query Examples

Resource `list` commands support the main OpenAlex query parameters:

```bash
uv run openalex-search-cli works list \
  --filter "publication_year:2024,type:article" \
  --search "machine learning" \
  --sort "-cited_by_count" \
  --per-page 10 \
  --select "id,display_name,cited_by_count"
```

Use `group_by` to get counts instead of records:

```bash
uv run openalex-search-cli works list \
  --filter "publication_year:2024" \
  --group-by "authorships.institutions.country_code"
```

Use cursor pagination for large result sets:

```bash
uv run openalex-search-cli works list --cursor "*" --per-page 100
```

Single-record `get` commands support `--select`:

```bash
uv run openalex-search-cli authors get A5023888391 --select "id,display_name,works_count"
```

Special endpoints have endpoint-specific commands:

```bash
uv run openalex-search-cli autocomplete search works --q "machine learning"
uv run openalex-search-cli text_topics classify --title "Graph neural networks" --abstract "We study..."
uv run openalex-search-cli rate_limit get
uv run openalex-search-cli changefiles get 2026-02-19
```
```

- [ ] **Step 2: Run help smoke checks**

Run:

```bash
make smoke
```

Expected: command exits successfully. Existing smoke output should include root help and sample list command output.

- [ ] **Step 3: Run syntax check**

Run:

```bash
make lint
```

Expected: command exits successfully.

- [ ] **Step 4: Commit**

Run:

```bash
git add README.md
git commit -m "docs: document rich OpenAlex query usage"
```

Expected: commit succeeds.

---

### Task 7: Final Verification

**Files:**
- No file changes unless a verification failure reveals a concrete defect.

- [ ] **Step 1: Run full local check**

Run:

```bash
make check
```

Expected: lint and tests pass.

- [ ] **Step 2: Verify help includes rich params**

Run:

```bash
uv run openalex-search-cli works list --help
```

Expected: output includes all list params: `--filter`, `--search`, `--sort`, `--group-by`, `--per-page`, `--page`, `--cursor`, `--sample`, `--select`.

- [ ] **Step 3: Verify special command help**

Run:

```bash
uv run openalex-search-cli autocomplete search --help
```

Expected: output includes `ENTITY_TYPE`, `--q`, and `--filter`.

- [ ] **Step 4: Inspect final diff**

Run:

```bash
git status --short
```

Expected: no uncommitted changes.

Run:

```bash
git log --oneline -5
```

Expected: recent commits include the commits from Tasks 1 through 6.

## Self-Review

- Spec coverage: Standard list/get resources cover `filter`, `search`, `sort`, `group_by`, `per_page`, `page`, `cursor`, `sample`, and `select`; special endpoints cover autocomplete, text topics, rate limit, and changefiles; missing spec endpoints are added.
- Placeholder scan: No step relies on undefined behavior or incomplete code.
- Type consistency: Shared helpers use `filter_` for Click callback variables and emit query key `filter`; Click exposes `--group-by` and emits query key `group_by`; ID path segments use `quote_path_segment`.
