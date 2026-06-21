.PHONY: help install install-dev lint format test run check clean smoke validate auth-check

PROJECT_NAME := openalex-search-cli

help:
	@echo "openalex-search-cli - Available commands"
	@echo ""
	@echo "  make install      Install dependencies with uv"
	@echo "  make install-dev  Install dependencies including dev extras"
	@echo "  make lint         Run basic lint checks"
	@echo "  make format       Format source code"
	@echo "  make test         Run tests"
	@echo "  make check        Run lint and tests"
	@echo "  make clean        Remove caches and build artifacts"
	@echo "  make smoke        Run quick CLI smoke checks"
	@echo "  make validate     Run live API read checks"
	@echo "  make auth-check   Verify OpenAlex API key access"
	@echo "  make run          Show CLI help"
	@echo ""
	@echo "  CLI examples:"
	@echo "  make works-list   Example: uv run $(PROJECT_NAME) works list"
	@echo "  make authors-list Example: uv run $(PROJECT_NAME) authors list"
	@echo "  make sources-list Example: uv run $(PROJECT_NAME) sources list"
	@echo "  make institutions-list Example: uv run $(PROJECT_NAME) institutions list"
	@echo "  make topics-list  Example: uv run $(PROJECT_NAME) topics list"
	@echo "  make keywords-list Example: uv run $(PROJECT_NAME) keywords list"
	@echo "  make publishers-list Example: uv run $(PROJECT_NAME) publishers list"
	@echo "  make funders-list Example: uv run $(PROJECT_NAME) funders list"

install:
	uv sync

install-dev:
	uv sync --all-extras

lint:
	uv run python -m py_compile src/*.py src/commands/*.py

format:
	uv run black src/
	uv run isort src/

test:
	uv run pytest tests/ -v

check: lint test

clean:
	rm -rf __pycache__ src/__pycache__ src/commands/__pycache__ tests/__pycache__ .pytest_cache .ruff_cache .mypy_cache .tox .nox htmlcov build dist *.egg-info .coverage .coverage.*

smoke:
	uv run $(PROJECT_NAME) --help
	uv run $(PROJECT_NAME) works list --format json
	uv run $(PROJECT_NAME) authors list --format json

validate:
	uv run $(PROJECT_NAME) works list
	uv run $(PROJECT_NAME) authors list
	uv run $(PROJECT_NAME) countries list

auth-check:
	uv run python -c "from src.config import Config; cfg = Config(); raise SystemExit(0 if cfg.get('api_key') else 1)"
	uv run $(PROJECT_NAME) rate_limit list

run:
	uv run $(PROJECT_NAME) --help

batch-example:
	uv run $(PROJECT_NAME) batch --input-file data/batch.csv --format json --output-path ./output

works-list:
	uv run $(PROJECT_NAME) works list

authors-list:
	uv run $(PROJECT_NAME) authors list

sources-list:
	uv run $(PROJECT_NAME) sources list

institutions-list:
	uv run $(PROJECT_NAME) institutions list

topics-list:
	uv run $(PROJECT_NAME) topics list

keywords-list:
	uv run $(PROJECT_NAME) keywords list

publishers-list:
	uv run $(PROJECT_NAME) publishers list

funders-list:
	uv run $(PROJECT_NAME) funders list

.DEFAULT_GOAL := help
