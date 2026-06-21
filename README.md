# OpenAlex Search CLI

Small Click-based CLI for the OpenAlex API.

## Links

- OpenAlex site: https://openalex.org
- OpenAlex documentation: https://developers.openalex.org
- Skillset repo: https://github.com/miguelfg/api-to-cli-skillset

## What It Does

- Lists core OpenAlex resources.
- Fetches single records by ID.
- Sends the OpenAlex `api_key` as a query parameter.
- Supports JSON output and batch entry points.

## Project Files

- `src/cli.py` - main CLI entry point
- `src/client.py` - API client
- `src/config.py` - `.env` loading
- `src/commands/` - resource commands
- `tests/` - smoke tests

## Requirements

- Python 3.10+
- `uv`

## Quick Start

```bash
uv sync
uv run openalex-search-cli --help
```

## Configuration

Create a `.env` file in the project root.

```env
OPENALEX_BASE_URL=https://api.openalex.org
OPENALEX_API_KEY=your_openalex_api_key
output_format=json
timestamp_format=%Y%m%d_%H%M%S
```

Notes:
- `.env` is loaded automatically.
- `.env.template` is only a starter file.
- `OPENALEX_API_KEY` is mapped to `api_key`.
- Environment variables override values from `.env`.

## Examples

List works:

```bash
uv run openalex-search-cli works list
```

List works in JSON:

```bash
uv run openalex-search-cli works list --format json
```

Get one work:

```bash
uv run openalex-search-cli works get W2741809807
```

List authors:

```bash
uv run openalex-search-cli authors list
```

List countries:

```bash
uv run openalex-search-cli countries list
```

## Batch Mode

Use the `batch` command for CSV or TXT input files.

```bash
uv run openalex-search-cli batch --input-file requests.csv
uv run openalex-search-cli batch --input-file requests.txt
```

## Available Commands

- `works`
- `authors`
- `sources`
- `institutions`
- `topics`
- `keywords`
- `publishers`
- `funders`
- `autocomplete`
- `domains`
- `fields`
- `subfields`
- `sdgs`
- `countries`
- `continents`
- `languages`
- `awards`
- `changefiles`
- `rate_limit`
- `text_topics`
- `batch`

## Validation

Run the built-in checks:

```bash
uv run pytest tests -v
make help
make test
```

## API Notes

- OpenAlex uses `api_key` in the query string.
- The loader accepts `OPENALEX_API_KEY` and maps it to `api_key`.
- Some endpoints work without a key, but limits are lower.
- `rate_limit` requires a valid key.

## License

OpenAlex data is published under CC0. Check the OpenAlex site for API terms and usage details.
