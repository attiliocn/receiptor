# receiptor
A parser for brazillian NFe written in Python

## Testing

This project uses `pytest` — a popular Python testing library. Tests live in the `tests/` folder and are split into three groups:

- `tests/unit/` — test individual functions in isolation (e.g. does `convert_to_float` handle `"1,07"` correctly?)
- `tests/integration/` — test the full pipeline end-to-end using real PDF files
- `tests/cli/` — test the command-line interface

Real PDF files used by tests are stored in `tests/fixtures/pdfs/`. A `manifest.json` file in that same `fixtures/` folder keeps a written record of what each fixture is and why it exists.

### Install dev dependencies

```bash
uv sync --group dev
```

### Run all tests

```bash
uv run pytest
```

### Run only one group

```bash
uv run pytest tests/unit
uv run pytest -m integration
uv run pytest -m cli
```

### Run a single test by name

```bash
uv run pytest tests/integration/test_pdf_pipeline.py::test_your_test_name -v
```

The `-v` flag makes the output more detailed, which is useful while debugging.

---

## How to add a test for a new problematic PDF

Use this workflow whenever you find a PDF that the parser handles incorrectly.

### Step 1 — Copy the PDF into the fixtures folder

```
tests/fixtures/pdfs/your_new_receipt.pdf
```

Pick a short, descriptive filename (no spaces). For example: `antonelli_march.pdf`.

### Step 2 — Register it in `manifest.json`

Open `tests/fixtures/manifest.json` and add an entry inside the `"fixtures"` array:

```json
{
  "id": "antonelli_march",
  "path": "tests/fixtures/pdfs/antonelli_march.pdf",
  "type": "pdf",
  "expected": {
    "status": "known_issue",
    "minimum_items": 0
  },
  "notes": "Describe what is wrong — e.g. items not extracted because layout differs"
}
```

The `"status": "known_issue"` just means you are documenting a bug, not that the test will automatically skip.

### Step 3 — Write the test

Open `tests/integration/test_pdf_pipeline.py` and add a new function at the bottom.

```python
@pytest.mark.integration
@pytest.mark.known_issue
def test_antonelli_march_extracts_items(fixtures_dir: Path, temp_output_csv: Path) -> None:
    pdf_path = fixtures_dir / "pdfs" / "antonelli_march.pdf"

    df = process_receipt(str(pdf_path), str(temp_output_csv))

    assert not df.empty
```

**What the lines mean:**

- `def test_...` — pytest automatically finds and runs any function whose name starts with `test_`. That is all you need to define a test.
- `@pytest.mark.integration` and `@pytest.mark.known_issue` — these lines starting with `@` are called *decorators*. They attach labels (called *markers*) to your test. Think of them as sticky notes. `integration` means "this test uses a real file", and `known_issue` means "this test is expected to fail right now because there is a known bug". The labels are used when you run `uv run pytest -m integration` to select only labelled tests. You do not need to understand the decorator mechanism deeply — just copy the pattern.
- `fixtures_dir` and `temp_output_csv` — these are *fixtures* (pytest's word for reusable helpers). They are defined in `tests/conftest.py` and pytest injects them automatically when a test function declares them as parameters. `fixtures_dir` gives you the path to `tests/fixtures/`, and `temp_output_csv` gives you a throwaway file path for the output CSV.
- `assert not df.empty` — `assert` is how you tell pytest what the correct result should be. If the condition after `assert` is false, the test fails. This particular line says: "I expect the parser to return at least one item."

### Step 4 — Run your new test and confirm it fails

```bash
uv run pytest tests/integration/test_pdf_pipeline.py::test_antonelli_march_extracts_items -v
```

You should see it fail. That confirms the test is actually catching the bug. Now you can work on fixing the parser.

### Step 5 — Fix the parser, then confirm the test passes

Once the bug is fixed, run the test again. When it passes, remove the `@pytest.mark.known_issue` line (the bug is no longer a known issue) and optionally tighten the assertion:

```python
assert len(df) == 12  # exact number of items expected in this receipt
```
