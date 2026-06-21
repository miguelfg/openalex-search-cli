# OpenAlex API Python Client

## Introduction

OpenAlex provides access to a large catalog of scholarly works, authors, sources, institutions, topics, keywords, publishers, funders, and related reference data.

This CLI client should make the OpenAlex API easy to use from the terminal for:
- list and get lookups on core entity resources
- search and filter exploration
- small batch retrieval jobs
- export of API responses for downstream analysis

**Base URL:** `https://api.openalex.org`
**API Version:** `1.0.0`
**Resources:** `works, authors, sources, institutions, topics, keywords, publishers, funders, autocomplete, domains, fields, subfields, sdgs, countries, continents, languages, awards, changefiles, rate_limit, text_topics`

## Implementation Decisions

- CLI Name: `openalex-search-cli`
- Python Version: `>=3.10`
- HTTP Library: `requests`
- Authentication: `OpenAlex API Key` query parameter from the OpenAlex API spec; optional and recommended for higher rate limits
- Credentials Configuration: `environment variables`
- Timeout: `30s total timeout`
- Retry Policy: `Enabled: 3 attempts, 1s base, x2 backoff, retry on 408,429,500,502,503,504`
- Output Formats: `json,csv,xlsx,sqlite`
- Output Accepted Formats and Default: `default_xlsx__accepted_xlsx_csv_sqlite`
- Batch Input Formats: `both`
- Default Save Data Mode: `timestamped`
- Lint/Format Toolchain: `ruff check --fix` + `ruff format`

## Purpose

The CLI should provide a stable, read-oriented interface for the most common OpenAlex workflows:
- retrieve a page of entities from a collection
- fetch a single entity by OpenAlex ID or supported external identifier
- search by text query where supported
- filter and sort result sets using documented OpenAlex query parameters

The project is intentionally centered on the documented GET endpoints. OpenAlex is effectively read-only from the CLI perspective for the covered resources.

## Installation

### System Requirements

- Python 3.10 or newer
- `uv`

### Install and Run

```bash
uv sync
uv run openalex-search-cli --help
```

## Configuration

Use environment variables in `.env` or the shell:

```bash
base_url=https://api.openalex.org
api_key=your_openalex_api_key
log_level=INFO
output_format=json
timestamp_format=%Y%m%d_%H%M%S
```

If no API key is configured, requests should still work at the public rate limit where permitted by OpenAlex.

## Authentication

OpenAlex uses an `API Key` query parameter named `api_key`.

The CLI should:
- read the key from configuration/environment
- attach it to every request as `api_key=...`
- avoid treating the key as an HTTP header

Recommended usage:

```bash
export api_key="your_openalex_api_key"
uv run openalex-search-cli works list
```

## Endpoint Reference

Common OpenAlex query parameters:
- `filter`
- `sort`
- `group_by`
- `search`
- `per_page`
- `page`
- `cursor`
- `sample`
- `select`
- `api_key`

### Works Resource

- `/works`
- `/works/{id}`

#### 1. List Works

Use `filter`, `sort`, `group_by`, `search`, `per_page`, `page`, `cursor`, `sample`, and `select`.

#### 2. Get Work

Accept OpenAlex IDs and supported external identifiers such as DOI formats documented by OpenAlex.

### Authors Resource

- `/authors`
- `/authors/{id}`

#### 1. List Authors

Use `filter`, `sort`, `group_by`, `search`, `per_page`, `page`, `cursor`, `sample`, and `select`.

#### 2. Get Author

Fetch a single author by OpenAlex ID or supported external identifier.

### Sources Resource

- `/sources`
- `/sources/{id}`

#### 1. List Sources

Use the documented list and filter parameters.

#### 2. Get Source

Fetch a single source by ID or supported external identifier.

### Institutions Resource

- `/institutions`
- `/institutions/{id}`

#### 1. List Institutions

Use the documented list and filter parameters.

#### 2. Get Institution

Fetch a single institution by ID or supported external identifier.

### Topics Resource

- `/topics`
- `/topics/{id}`

#### 1. List Topics

Use the documented list and filter parameters.

#### 2. Get Topic

Fetch a single topic by ID.

### Keywords Resource

- `/keywords`
- `/keywords/{id}`

#### 1. List Keywords

Use the documented list and filter parameters.

#### 2. Get Keyword

Fetch a single keyword by ID.

### Publishers Resource

- `/publishers`
- `/publishers/{id}`

#### 1. List Publishers

Use the documented list and filter parameters.

#### 2. Get Publisher

Fetch a single publisher by ID.

### Funders Resource

- `/funders`
- `/funders/{id}`

#### 1. List Funders

Use the documented list and filter parameters.

#### 2. Get Funder

Fetch a single funder by ID.

### Autocomplete Resource

- `/autocomplete/{entity_type}`

#### 1. Autocomplete Search

Use `entity_type`, `q`, and `filter` where documented.

### Utility Resources

- `/rate-limit`
- `/changefiles`
- `/changefiles/{date}`
- `/domains`
- `/domains/{id}`
- `/fields`
- `/fields/{id}`
- `/subfields`
- `/subfields/{id}`
- `/sdgs`
- `/sdgs/{id}`
- `/countries`
- `/countries/{id}`
- `/continents`
- `/continents/{id}`
- `/languages`
- `/languages/{id}`
- `/awards`
- `/awards/{id}`
- `/text/topics`

#### 1. Rate Limit Status

Use `/rate-limit` to inspect the current limit state.

#### 2. Changefile Dates

Use `/changefiles` and `/changefiles/{date}` for changefile discovery and retrieval.

#### 3. Taxonomy and Reference Data

Use the entity list/get endpoints for domains, fields, subfields, SDGs, countries, continents, languages, and awards.

#### 4. Text Topic Classification

Use `/text/topics` with `title` and `abstract` inputs for aboutness classification.

## Input/Output Examples

### Works Lookup

```bash
uv run openalex-search-cli works list --per-page 10
uv run openalex-search-cli works get W2741809807
```

### Author Search

```bash
uv run openalex-search-cli authors list --filter "display_name.search:Einstein" --per-page 10
```

### Text Topic Classification

```bash
uv run openalex-search-cli text_topics list
```

## Error Handling

- Return a clear message for invalid IDs or malformed filters
- Preserve HTTP status and response body for API errors where useful
- Surface 429 responses with retry-aware messaging
- Fail fast if the API key is required for the requested workflow and missing from configuration

## Logging

- Default to concise informational logging
- Enable verbose request/response diagnostics with `--verbose`
- Avoid logging secrets or full query strings that include credentials

## Validation Requirements

The generated CLI project must perform low-volume live validation for read commands.

Required validation behavior:
- run list or get requests against representative GET endpoints
- keep result volume small, preferably `per_page=10`
- use documented OpenAlex parameter names rather than invented flags
- validate at least one endpoint each for works, authors, and one utility resource
- treat these live checks as required acceptance criteria

## Makefile and Project Management

The generated project should include:
- `make help`
- `make test`
- per-resource list targets for quick smoke checks

Preferred workflow:

```bash
uv sync
uv run openalex-search-cli --help
uv run openalex-search-cli works list --per-page 10
uv run openalex-search-cli authors list --per-page 10
```

## Notes and Constraints

- OpenAlex rate limits vary with and without an API key.
- The CLI should prioritize read-only coverage and not invent write behavior.
- Deprecated OpenAlex endpoints such as `/concepts` should not be treated as primary commands.
