from __future__ import annotations

import numpy as np

from receiptor import create_dataframe


def test_create_dataframe_empty_items() -> None:
    df = create_dataframe([])

    assert df.empty


def test_create_dataframe_expected_columns_and_types() -> None:
    items = [
        {
            "item_name": "ARROZ",
            "quantity": "1,000",
            "unit": "KG",
            "unit_price": "7,99",
        }
    ]

    df = create_dataframe(items)

    assert list(df.columns) == [
        "item_name",
        "quantity",
        "unit",
        "unit_price",
        "quantity_float",
        "unit_price_float",
    ]
    assert df.loc[0, "quantity_float"] == 1.0
    assert df.loc[0, "unit_price_float"] == 7.99


def test_create_dataframe_partial_conversion_failure() -> None:
    items = [
        {
            "item_name": "INVALID PRICE",
            "quantity": "1,000",
            "unit": "UN",
            "unit_price": "oops",
        }
    ]

    df = create_dataframe(items)

    assert df.loc[0, "quantity_float"] == 1.0
    assert np.isnan(df.loc[0, "unit_price_float"])
