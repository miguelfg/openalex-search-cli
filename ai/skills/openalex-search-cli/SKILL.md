---
name: openalex-search-cli
description: >-
  This skill should be used to query the OpenAlex API through this project's
  Click-based CLI. Use it whenever the user wants to list OpenAlex resources
  (works, authors, sources, institutions, topics, funders, publishers, etc.)
  or fetch a single OpenAlex record by ID. Runs the CLI under `uv` and reads
  an optional `.env` for the API key. Triggers on requests like "list works",
  "get author A5023888391", "look up this OpenAlex ID", or "query OpenAlex".
---

# OpenAlex Search CLI

## Purpose

Drive the local `openalex-search-cli` (a thin Click wrapper over the OpenAlex
REST API) to list resources or fetch single records by ID. Output is JSON.

## Setup

Run everything from the project root (where `pyproject.toml` lives):
`/home/miguelfg/workspace/projects/openalex-search-cli`. `uv` resolves the
project and its dependencies automatically.

```bash
uv sync                              # once, installs deps
uv run openalex-search-cli --help    # verify it works
```

An API key is **optional**. Most reads work without one at lower rate limits.
To use a key, create a `.env` in the project root (auto-loaded regardless of
current directory):

```env
OPENALEX_BASE_URL=https://api.openalex.org
OPENALEX_API_KEY=your_openalex_api_key
```

`OPENALEX_API_KEY` is mapped to the `api_key` query param. Real environment
variables override `.env`.

## Running queries

Every resource group exposes exactly two operations:

```bash
# List the first page of a resource (JSON)
uv run openalex-search-cli <resource> list

# Fetch one record by its OpenAlex ID
uv run openalex-search-cli <resource> get <ID>
```

Examples:

```bash
uv run openalex-search-cli works list
uv run openalex-search-cli works get W2741809807
uv run openalex-search-cli authors get A5023888391
uv run openalex-search-cli sources list
uv run openalex-search-cli countries list
```

### Resources

`works`, `authors`, `sources`, `institutions`, `topics`, `keywords`,
`publishers`, `funders`, `autocomplete`, `domains`, `fields`, `subfields`,
`sdgs`, `countries`, `continents`, `languages`, `awards`, `changefiles`,
`rate_limit`, `text_topics`.

`rate_limit list` requires a valid API key (use it to verify auth).

## Output

`list`/`get` emit JSON to stdout. `--format` accepts `json` only in practice;
`csv`/`xlsx` are stubs that print "not yet implemented". To post-process, pipe
JSON to `jq` (e.g. `... works list | jq '.results[].id'`).

## Batch mode

For many lookups, feed a file of raw GET paths:

```bash
uv run openalex-search-cli batch --input-file requests.csv --format json --output-path ./output
```

- CSV: header row, columns `method,endpoint` (`method` must be `GET`).
- TXT: one JSON object per line, e.g. `{"method": "GET", "endpoint": "/works/W2741809807"}`.
- Endpoints must be rooted API paths (`/works/...`). The client rejects
  off-host, `..`, and `?`/`#` — so **query-string filters are not supported**
  through batch.
- Batch (and only batch) can also write `csv`/`xlsx`/`sqlite` output.

## Limitations (important — do not invent flags)

- The CLI exposes **no filter, search, sort, or pagination options**. `list`
  returns the API's default first page; `get` needs an exact OpenAlex ID.
- There are no write operations (OpenAlex is read-only).
- For filtered/faceted OpenAlex queries the CLI cannot express, tell the user
  to hit the API directly (`https://api.openalex.org/works?filter=...`) rather
  than fabricating CLI flags.

## Troubleshooting

- `Unsafe endpoint: ...` — the ID or batch path contained `..`, `?`, `#`, a
  scheme, or a leading `//`. Pass a bare ID or a clean `/resource/ID` path.
- Auth failures on `rate_limit` — check `.env` has `OPENALEX_API_KEY`
  (`uv run openalex-search-cli rate_limit list` to confirm).
- Command not found — run from the project root so `uv` finds the project.
