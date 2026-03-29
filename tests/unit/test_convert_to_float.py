from __future__ import annotations

import numpy as np
import pytest

from receiptor import convert_to_float


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("1.234,56", 1234.56),
        ("1234,56", 1234.56),
        ("0,01", 0.01),
        ("  10,00  ", 10.0),
        ("1.000", 1000.0),
        # Current implementation removes all dots before parsing.
        ("1.2.3,4", 123.4),
    ],
)
def test_convert_to_float_valid_values(raw: str, expected: float) -> None:
    assert convert_to_float(raw) == pytest.approx(expected)


@pytest.mark.parametrize("raw", [None, "", "abc", 42])
def test_convert_to_float_invalid_values(raw: object) -> None:
    result = convert_to_float(raw)  # type: ignore[arg-type]
    assert np.isnan(result)
