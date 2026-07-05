# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Uses `uv` and a Makefile. Run `make help` for the full list.

- `make install` / `make install-dev` — `uv sync` (dev adds pytest, ruff, black, isort)
- `make test` — `uv run pytest tests/ -v`
- Single test: `uv run pytest tests/test_cli.py::test_root_help -v`
- `make lint` — `py_compile` on all sources (no ruff/mypy gate; syntax check only)
- `make format` — `black` + `isort` on `src/`
- `make check` — lint + test
- `make smoke` — runs `--help` and a couple `list` commands (needs no key)
- `make validate` — live API read calls; `make auth-check` — verifies `api_key` is set and hits `rate_limit`
- Run the CLI: `uv run openalex-search-cli <resource> <list|get|create> ...`

## Architecture

Click-based CLI wrapping the OpenAlex API. **This project was auto-generated** from `docs/openalex_search_cli_PRD.md` by the skillset at https://github.com/miguelfg/api-to-cli-skillset — hence the uniform, boilerplate-heavy command modules.

Flow: `src/cli.py` (root group, registers ~20 resource groups + `batch`) → `src/commands/<resource>_commands.py` (per-resource Click group) → `src/client.py` `APIClient` → OpenAlex.

- **Package layout:** imports use the `src.` prefix (`from src.config import Config`); entry point is `src.cli:cli`. Keep this — don't rewrite to bare `config`.
- **Config** (`src/config.py`): loads `.env` from project root. Normalizes `OPENALEX_API_KEY` → `api_key` and `OPENALEX_BASE_URL` → `base_url`. Real env vars override `.env` values.
- **Auth is a query param, not a header.** `APIClient._setup_auth` is intentionally a no-op; `_request` appends `api_key` to the query string. HTTP errors are re-raised with the URL stripped of params to avoid leaking the key — preserve that redaction.
- **Per-command output:** each `<resource> list`/`get` only implements `--format json`; `csv`/`xlsx` print "not yet implemented". Real multi-format export lives in `src/output.py` `save_output` (json/csv/xlsx/sqlite, pandas-backed) and is used **only** by the `batch` command.
- **Batch** (`src/batch_processor.py`): `--input-file` is CSV (columns `method,endpoint,data` per row) or TXT (one JSON object per line). Endpoints are raw API paths. Results go to `--output-path` via `save_output`.

## Adding a resource command

Match the existing pattern: create `src/commands/<name>_commands.py` with a `<name>_group` Click group exposing `list`/`get`/`create`, then register it in `src/cli.py` with `cli.add_command(<name>_group, '<name>')`. Because the modules are generated boilerplate, prefer regenerating via the skillset over hand-editing many files if the change is broad.

## Notes

- Tests (`tests/test_cli.py`) are smoke tests only (help output, dependency presence) — not behavioral coverage.
- `.env` is gitignored; `.env.example` documents the keys, `.env.template` is a minimal starter.
