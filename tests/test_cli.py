"""
Basic CLI smoke tests for generated projects.
"""

import importlib.util

from click.testing import CliRunner

from src.cli import cli


def test_root_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "batch" in result.output


def test_batch_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["batch", "--help"])
    assert result.exit_code == 0


def test_selected_http_library_dependency_is_available():
    assert importlib.util.find_spec("requests") is not None


def test_endpoint_guard_rejects_unsafe_paths():
    import pytest

    from src.client import APIClient

    APIClient._validate_endpoint("/works/W123")  # safe path passes
    for bad in [
        "//evil.com",
        "/works/../authors",
        "https://evil.com",
        "/works/W1?x=y",
        "/works/%2f..",
        "/works/ id",
    ]:
        with pytest.raises(ValueError):
            APIClient._validate_endpoint(bad)


def test_http_errors_do_not_expose_query_string(monkeypatch):
    import pytest
    import requests

    from src.client import APIClient
    from src.config import Config

    class FakeResponse:
        status_code = 400
        reason = "Bad Request"
        text = "bad"

        def raise_for_status(self):
            raise requests.HTTPError(
                "400 Client Error for url: https://api.openalex.org/works?api_key=SECRET"
            )

    def fake_request(**kwargs):
        return FakeResponse()

    client = APIClient(Config())
    client.api_key = "SECRET"
    monkeypatch.setattr(client.session, "request", fake_request)

    with pytest.raises(requests.HTTPError) as excinfo:
        client.get("/works")

    assert "api_key" not in str(excinfo.value)
    assert "SECRET" not in str(excinfo.value)
    assert (
        str(excinfo.value) == "400 Bad Request for GET https://api.openalex.org/works"
    )


def test_works_list_passes_recipe_query_params(monkeypatch):
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
            "CRISPR",
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
            "--seed",
            "42",
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
                "search": "CRISPR",
                "sort": "cited_by_count:desc",
                "group_by": "publication_year",
                "per_page": 50,
                "page": 2,
                "cursor": "*",
                "sample": 10,
                "select": "id,display_name",
                "seed": 42,
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
    result = runner.invoke(
        cli, ["works", "get", "W2741809807", "--select", "id,display_name"]
    )

    assert result.exit_code == 0
    assert calls == [("/works/W2741809807", {"select": "id,display_name"})]
    assert "Example" in result.output


def test_autocomplete_search_passes_entity_and_query(monkeypatch):
    calls = []

    def fake_get(self, endpoint, params=None):
        calls.append((endpoint, params))
        return {"results": [{"display_name": "Elsevier"}]}

    monkeypatch.setattr("src.client.APIClient.get", fake_get)

    runner = CliRunner()
    result = runner.invoke(
        cli, ["autocomplete", "search", "publishers", "--q", "elsevier"]
    )

    assert result.exit_code == 0
    assert calls == [("/autocomplete/publishers", {"q": "elsevier"})]
    assert "Elsevier" in result.output
