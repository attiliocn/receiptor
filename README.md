# receiptor
A parser for brazillian NFe written in Python

## Testing

This project uses `pytest` for unit, integration, and CLI regression coverage.

### Install

```bash
uv sync --group dev
```

This creates or updates `uv.lock` and installs runtime + dev dependencies.

### Run tests

```bash
uv run pytest
```

### Run by level

```bash
uv run pytest tests/unit
uv run pytest -m integration
uv run pytest -m cli
```

## Regression fixture workflow

1. Add problematic receipts to `tests/fixtures/pdfs/`.
2. If a PDF cannot be shared, add a sanitized parser text fixture to `tests/fixtures/text/`.
3. Register the fixture intent in `tests/fixtures/manifest.json`.
4. Add a failing test first, then fix parser behavior.
