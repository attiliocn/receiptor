from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from receiptor import extract_text_from_pdf, process_receipt


@pytest.mark.integration
def test_extract_text_from_pdf_non_empty(fixtures_dir: Path) -> None:
    pdf_path = fixtures_dir / "pdfs" / "paraiso_baseline.pdf"

    text = extract_text_from_pdf(str(pdf_path))

    assert isinstance(text, str)
    assert text.strip() != ""


@pytest.mark.integration
def test_process_receipt_creates_output_and_columns(fixtures_dir: Path, temp_output_csv: Path) -> None:
    pdf_path = fixtures_dir / "pdfs" / "paraiso_baseline.pdf"

    df = process_receipt(str(pdf_path), str(temp_output_csv))

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert temp_output_csv.exists()
    assert {
        "item_name",
        "quantity",
        "unit",
        "unit_price",
        "quantity_float",
        "unit_price_float",
    }.issubset(df.columns)


@pytest.mark.integration
@pytest.mark.known_issue
def test_process_receipt_variant_layout_regression(fixtures_dir: Path, temp_output_csv: Path) -> None:
    pdf_path = fixtures_dir / "pdfs" / "antonelli_variant.pdf"

    df = process_receipt(str(pdf_path), str(temp_output_csv))

    assert not df.empty
