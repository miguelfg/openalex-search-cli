# OpenAlex Search CLI Cookbook

Practical examples for `openalex-search-cli`, based on the OpenAlex recipe page archived at
[`docs/openalex-recipes.md`](docs/openalex-recipes.md).

Run examples from the project root:

```bash
uv run openalex-search-cli <resource> <command> [options]
```

Most read calls work without a key. Put `OPENALEX_API_KEY=...` in `.env` for higher limits and paid content features.

## Core Patterns

List a resource:

```bash
uv run openalex-search-cli works list --per-page 5
```

Fetch one record:

```bash
uv run openalex-search-cli works get W2741809807
```

Return only fields you need:

```bash
uv run openalex-search-cli works get W2741809807 \
  --select id,display_name,publication_year,cited_by_count
```

Sort descending with the OpenAlex shorthand from the docs:

```bash
uv run openalex-search-cli works list \
  --filter publication_year:2024 \
  --sort -cited_by_count \
  --per-page 10
```

The CLI normalizes `--sort -field` to the live API form `field:desc`.

## Works

Find works by an author:

```bash
uv run openalex-search-cli works list \
  --filter author.id:A5023888391 \
  --sort -publication_date \
  --per-page 10 \
  --select id,display_name,publication_year
```

Find highly cited works by an author:

```bash
uv run openalex-search-cli works list \
  --filter 'author.id:A5023888391,cited_by_count:>10' \
  --sort -cited_by_count \
  --per-page 10 \
  --select id,display_name,cited_by_count
```

Find works from an institution:

```bash
uv run openalex-search-cli works list \
  --filter institutions.id:I136199984 \
  --sort -publication_date \
  --per-page 10 \
  --select id,display_name,publication_year
```

Find open access works from MIT since 2020:

```bash
uv run openalex-search-cli works list \
  --filter 'institutions.id:I63966007,open_access.is_oa:true,publication_year:>2019' \
  --per-page 10 \
  --select id,display_name,publication_year
```

Find works on a topic:

```bash
uv run openalex-search-cli works list \
  --filter topics.id:T10000 \
  --sort -cited_by_count \
  --per-page 10 \
  --select id,display_name,cited_by_count
```

Search by keyword:

```bash
uv run openalex-search-cli works list \
  --search CRISPR \
  --sort -relevance_score \
  --per-page 10 \
  --select id,display_name,relevance_score
```

Find works that cite a paper:

```bash
uv run openalex-search-cli works list \
  --filter cites:W2741809807 \
  --sort -publication_date \
  --per-page 10 \
  --select id,display_name,publication_year
```

Find international collaborations:

```bash
uv run openalex-search-cli works list \
  --filter 'institutions.country_code:IN,countries_distinct_count:>1,type:article' \
  --per-page 10 \
  --select id,display_name,publication_year
```

## Trends And Counts

Count works per year:

```bash
uv run openalex-search-cli works list \
  --filter publication_year:2020-2024 \
  --group-by publication_year
```

Count open access works per year:

```bash
uv run openalex-search-cli works list \
  --filter 'publication_year:2020-2024,open_access.is_oa:true' \
  --group-by publication_year
```

Sample reproducibly:

```bash
uv run openalex-search-cli works list \
  --filter publication_year:2024 \
  --sample 100 \
  --seed 42 \
  --per-page 100
```

## Open Access And Full Text

Find all OA works from 2024:

```bash
uv run openalex-search-cli works list \
  --filter 'publication_year:2024,open_access.is_oa:true' \
  --per-page 10
```

Find gold OA works:

```bash
uv run openalex-search-cli works list \
  --filter open_access.oa_status:gold \
  --per-page 10
```

Find works with CC-BY licenses:

```bash
uv run openalex-search-cli works list \
  --filter best_oa_location.license:cc-by \
  --per-page 10
```

Find works with downloadable PDFs:

```bash
uv run openalex-search-cli works list \
  --filter has_content.pdf:true \
  --per-page 10 \
  --select id,display_name,content_urls
```

Find works with abstracts:

```bash
uv run openalex-search-cli works list \
  --filter has_abstract:true \
  --per-page 10 \
  --select id,display_name,abstract_inverted_index
```

Paid PDF downloads are outside this CLI. Use OpenAlex's content endpoint or `openalex-official` for bulk downloads.

## Institutions, Sources, Authors

Rank US universities by citation count:

```bash
uv run openalex-search-cli institutions list \
  --filter country_code:US,type:education \
  --sort -cited_by_count \
  --per-page 20 \
  --select id,display_name,works_count,cited_by_count
```

Find top journals by work count:

```bash
uv run openalex-search-cli sources list \
  --filter type:journal \
  --sort -works_count \
  --per-page 20 \
  --select id,display_name,works_count
```

Find open access journals:

```bash
uv run openalex-search-cli sources list \
  --filter type:journal,is_oa:true \
  --sort -works_count \
  --per-page 20 \
  --select id,display_name,works_count,is_oa
```

Find co-authors by concept overlap:

```bash
uv run openalex-search-cli authors list \
  --filter x_concepts.id:C41008148 \
  --sort -works_count \
  --per-page 10 \
  --select id,display_name,works_count
```

## Batch-Like ID Fetching

Fetch multiple works with the OR operator:

```bash
uv run openalex-search-cli works list \
  --filter 'openalex:W2100837269|W2134720587' \
  --per-page 100 \
  --select id,display_name
```

Fetch multiple works by DOI:

```bash
uv run openalex-search-cli works list \
  --filter 'doi:https://doi.org/10.1234/a|https://doi.org/10.1234/b' \
  --per-page 100
```

The `batch` command is best for simple raw path lookups such as `/works/W2741809807`. It intentionally rejects query strings.

## Funders

Find a funder by name:

```bash
uv run openalex-search-cli funders list \
  --search "national institutes of health" \
  --per-page 5 \
  --select id,display_name
```

Filter works funded by NIH:

```bash
uv run openalex-search-cli works list \
  --filter awards.funder_id:F4320306076 \
  --sort -publication_date \
  --per-page 10 \
  --select id,display_name,publication_year
```

Filter works by grant number:

```bash
uv run openalex-search-cli works list \
  --filter awards.funder_id:F4320306076,awards.funder_award_id:R01-GM123456 \
  --per-page 10
```

Find funded OA works from 2024:

```bash
uv run openalex-search-cli works list \
  --filter 'awards.funder_id:F4320306076,publication_year:2024,open_access.is_oa:true' \
  --sort -cited_by_count \
  --per-page 10
```

## Publishers

Search for a publisher:

```bash
uv run openalex-search-cli publishers list \
  --search elsevier \
  --per-page 5 \
  --select id,display_name,works_count
```

Inspect publisher hierarchy:

```bash
uv run openalex-search-cli publishers get P4310319965 \
  --select id,display_name,hierarchy_level,lineage
```

List subsidiaries of a parent publisher:

```bash
uv run openalex-search-cli publishers list \
  --filter parent_publisher:P4310319965 \
  --sort -works_count \
  --per-page 20 \
  --select id,display_name,works_count
```

List top-level publishers:

```bash
uv run openalex-search-cli publishers list \
  --filter hierarchy_level:0 \
  --sort -works_count \
  --per-page 20 \
  --select id,display_name,works_count
```

## Citation Networks

Inspect citation fields on a work:

```bash
uv run openalex-search-cli works get W2741809807 \
  --select id,display_name,referenced_works,cited_by_api_url,related_works
```

Follow outgoing citations:

```bash
uv run openalex-search-cli works list \
  --filter 'openalex:W2100837269|W2134720587' \
  --per-page 100 \
  --select id,display_name
```

Follow incoming citations:

```bash
uv run openalex-search-cli works list \
  --filter cites:W2741809807 \
  --sort -publication_date \
  --per-page 10 \
  --select id,display_name,publication_year
```

Fetch related works:

```bash
uv run openalex-search-cli works list \
  --filter 'openalex:W2052533833|W1982351946' \
  --per-page 100 \
  --select id,display_name
```

## Autocomplete

Autocomplete publishers:

```bash
uv run openalex-search-cli autocomplete search publishers --q elsevier
```

Autocomplete institutions:

```bash
uv run openalex-search-cli autocomplete search institutions --q harvard
```

## Output Tips

Pretty-print selected values with `jq`:

```bash
uv run openalex-search-cli works list \
  --search CRISPR \
  --per-page 5 \
  --select id,display_name \
  | jq -r '.results[] | [.id, .display_name] | @tsv'
```

Save output:

```bash
uv run openalex-search-cli works list \
  --filter publication_year:2024 \
  --per-page 100 \
  > works-2024.json
```

Check rate limits when a key is configured:

```bash
uv run openalex-search-cli rate_limit get
```
