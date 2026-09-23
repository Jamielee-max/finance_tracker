"""
Tests for transform.py.

Split into two groups:
  - categorise(): the keyword-matching logic, tested word by word.
  - transform(): the DataFrame-level cleaning/derivation logic.
"""

import pandas as pd
import pytest

from transform import categorise, transform


# ---------------------------------------------------------------------
# categorise()
# ---------------------------------------------------------------------

@pytest.mark.parametrize(
    "description, expected_category",
    [
        ("Checkers Grocery", "grocery"),
        ("WOOLWORTHS", "grocery"),  # case-insensitive
        ("Uber Trip", "transport"),
        ("Uber Eats", "food"),  # more specific match than "transport"
        ("Netflix Subscription", "subscriptions"),
        ("Takealot Order", "shopping"),
        ("Rent Payment", "housing"),
        ("Salary Deposit", "income"),
    ],
)
def test_categorise_known_keywords(description, expected_category):
    assert categorise(description) == expected_category


def test_categorise_unknown_defaults_to_other():
    assert categorise("Some Random Shop") == "other"


def test_categorise_is_case_insensitive():
    assert categorise("checkers grocery") == categorise("CHECKERS GROCERY")


# ---------------------------------------------------------------------
# transform()
# ---------------------------------------------------------------------

def _raw_df(**overrides) -> pd.DataFrame:
    """Build a minimal one-row raw DataFrame, with optional overrides."""
    row = {
        "date": "2026-01-01",
        "description": "Uber Trip",
        "amount": -50.0,
    }
    row.update(overrides)
    return pd.DataFrame([row])


def test_transform_adds_expected_columns():
    result = transform(_raw_df())
    for column in ("category", "type", "month"):
        assert column in result.columns


def test_transform_marks_negative_amount_as_expense():
    result = transform(_raw_df(amount=-50.0))
    assert result.loc[0, "type"] == "expense"


def test_transform_marks_positive_amount_as_income():
    result = transform(_raw_df(amount=15000.0))
    assert result.loc[0, "type"] == "income"


def test_transform_marks_zero_amount_as_neutral():
    result = transform(_raw_df(amount=0.0))
    assert result.loc[0, "type"] == "neutral"


def test_transform_converts_date_to_datetime():
    result = transform(_raw_df(date="2026-01-01"))
    assert pd.api.types.is_datetime64_any_dtype(result["date"])


def test_transform_derives_month_as_year_month_string():
    result = transform(_raw_df(date="2026-03-15"))
    assert result.loc[0, "month"] == "2026-03"


def test_transform_drops_rows_with_missing_amount():
    raw = pd.DataFrame(
        [
            {"date": "2026-01-01", "description": "Uber Trip", "amount": -50.0},
            {"date": "2026-01-02", "description": "Mystery Row", "amount": None},
        ]
    )
    result = transform(raw)
    assert len(result) == 1


def test_transform_does_not_mutate_input():
    raw = _raw_df()
    original_columns = list(raw.columns)
    transform(raw)
    assert list(raw.columns) == original_columns