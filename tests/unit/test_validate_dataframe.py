from __future__ import annotations

import pandas as pd

from receiptor import validate_dataframe


def test_validate_dataframe_empty_reports_warning(capsys) -> None:
    validate_dataframe(pd.DataFrame())

    captured = capsys.readouterr()
    assert "DataFrame is empty" in captured.out


def test_validate_dataframe_reports_invalid_values(capsys) -> None:
    df = pd.DataFrame(
        [
            {
                "item_name": "TEST ITEM",
                "quantity": "1,000",
                "unit": "UN",
                "unit_price": "3,50",
                "quantity_float": 0.0,
                "unit_price_float": -1.0,
            },
            {
                "item_name": "BROKEN",
                "quantity": "oops",
                "unit": "UN",
                "unit_price": "oops",
                "quantity_float": float("nan"),
                "unit_price_float": float("nan"),
            },
        ]
    )

    validate_dataframe(df)

    captured = capsys.readouterr()
    assert "invalid quantity values" in captured.out
    assert "invalid unit_price values" in captured.out
    assert "Found quantity <= 0" in captured.out
