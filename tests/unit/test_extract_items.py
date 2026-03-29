from __future__ import annotations

from pathlib import Path

import pytest

from receiptor import extract_items


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_extract_items_single_match(fixtures_dir: Path) -> None:
    text = _read_text(fixtures_dir / "text" / "valid_item.txt")

    items = extract_items(text)

    assert len(items) == 1
    assert items[0]["item_name"] == "ARROZ BRANCO TIPO 1"
    assert items[0]["quantity"] == "1,000"
    assert items[0]["unit"] == "KG"
    assert items[0]["unit_price"] == "7,99"


def test_extract_items_multiple_matches(fixtures_dir: Path) -> None:
    text = _read_text(fixtures_dir / "text" / "multi_item.txt")

    items = extract_items(text)

    assert len(items) == 2
    assert [entry["item_name"] for entry in items] == ["ARROZ BRANCO TIPO 1", "FEIJAO PRETO"]


def test_extract_items_no_match() -> None:
    text = "This is not a receipt item block"

    items = extract_items(text)

    assert items == []


def test_extract_items_with_comma_in_name(fixtures_dir: Path) -> None:
    text = _read_text(fixtures_dir / "text" / "item_with_comma.txt")

    items = extract_items(text)

    assert len(items) == 1
    assert items[0]["item_name"] == "CARNE, VERMELHA"
    assert items[0]["quantity"] == "1,500"
    assert items[0]["unit"] == "KG"
    assert items[0]["unit_price"] == "25,50"


def test_extract_items_with_percent_in_name(fixtures_dir: Path) -> None:
    text = _read_text(fixtures_dir / "text" / "item_with_percent.txt")

    items = extract_items(text)

    assert len(items) == 1
    assert items[0]["item_name"] == "DESCONTO 50%"
    assert items[0]["quantity"] == "1,000"
    assert items[0]["unit"] == "UN"
    assert items[0]["unit_price"] == "10,00"


def test_extract_items_with_comma_and_percent_in_name(fixtures_dir: Path) -> None:
    text = _read_text(fixtures_dir / "text" / "item_with_comma_and_percent.txt")

    items = extract_items(text)

    assert len(items) == 1
    assert items[0]["item_name"] == "PRODUTO, DESC. 25%"
    assert items[0]["quantity"] == "2,000"
    assert items[0]["unit"] == "UN"
    assert items[0]["unit_price"] == "15,99"


def test_extract_items_ignores_address_before_item(fixtures_dir: Path) -> None:
    text = _read_text(fixtures_dir / "text" / "address_before_item.txt")

    items = extract_items(text)

    assert len(items) == 1
    assert items[0]["item_name"] == "ARROZ BRANCO TIPO 1"
    assert items[0]["quantity"] == "1,000"
    assert items[0]["unit"] == "KG"
    assert items[0]["unit_price"] == "7,99"


def test_extract_items_ignores_multiple_addresses_before_item(fixtures_dir: Path) -> None:
    text = _read_text(fixtures_dir / "text" / "multiple_addresses_before_item.txt")

    items = extract_items(text)

    assert len(items) == 1
    assert items[0]["item_name"] == "PRODUTO COM VIRGULA, VARIANTE"
    assert items[0]["quantity"] == "0,500"
    assert items[0]["unit"] == "KG"
    assert items[0]["unit_price"] == "22,75"


@pytest.mark.known_issue
@pytest.mark.xfail(reason="Current regex requires item names to begin with uppercase", strict=False)
def test_extract_items_mixed_case_known_limitation(fixtures_dir: Path) -> None:
    text = _read_text(fixtures_dir / "text" / "mixed_case_item.txt")

    items = extract_items(text)

    assert len(items) == 1
