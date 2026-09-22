"""
Tests for report.py.

Each test builds its own tiny SQLite db inside tmp_path (same table
shape that load.py produces) so these never touch the real budget.db.
"""

import sqlite3

import pandas as pd
import pytest

from report import spending_by_category, income_vs_expense, monthly_summary


def _make_db(tmp_path, rows) -> str:
    """Write `rows` (list of dicts) into a throwaway transactions table."""
    db_path = str(tmp_path / "budget.db")
    conn = sqlite3.connect(db_path)
    pd.DataFrame(rows).to_sql("transactions", conn, if_exists="replace", index=False)
    conn.close()
    return db_path


SAMPLE_ROWS = [
    {"date": "2026-01-03", "description": "Checkers Grocery", "amount": -540.20,
     "category": "grocery", "type": "expense", "month": "2026-01"},
    {"date": "2026-01-04", "description": "Uber Trip", "amount": -85.00,
     "category": "transport", "type": "expense", "month": "2026-01"},
    {"date": "2026-01-05", "description": "Salary Deposit", "amount": 15000.00,
     "category": "income", "type": "income", "month": "2026-01"},
    {"date": "2026-02-09", "description": "Woolworths", "amount": -320.75,
     "category": "grocery", "type": "expense", "month": "2026-02"},
]


# 
# spending_by_category()
# 

def test_spending_by_category_returns_dataframe(tmp_path):
    db_path = _make_db(tmp_path, SAMPLE_ROWS)
    result = spending_by_category(db_path)
    assert isinstance(result, pd.DataFrame)


def test_spending_by_category_sums_correctly(tmp_path):
    db_path = _make_db(tmp_path, SAMPLE_ROWS)
    result = spending_by_category(db_path).set_index("category")
    assert result.loc["grocery", "total"] == pytest.approx(-860.95)


def test_spending_by_category_excludes_income(tmp_path):
    db_path = _make_db(tmp_path, SAMPLE_ROWS)
    result = spending_by_category(db_path)
    assert "income" not in result["category"].values


# 
# income_vs_expense()
# 

def test_income_vs_expense_returns_dict(tmp_path):
    db_path = _make_db(tmp_path, SAMPLE_ROWS)
    result = income_vs_expense(db_path)
    assert isinstance(result, dict)


def test_income_vs_expense_totals(tmp_path):
    db_path = _make_db(tmp_path, SAMPLE_ROWS)
    result = income_vs_expense(db_path)
    assert result["income"] == pytest.approx(15000.00)
    assert result["expense"] == pytest.approx(-945.95)


def test_income_vs_expense_missing_type_defaults_to_zero(tmp_path):
    db_path = _make_db(tmp_path, [SAMPLE_ROWS[0]])  # only an expense row
    result = income_vs_expense(db_path)
    assert result["income"] == 0


# 
# monthly_summary()
# 

def test_monthly_summary_returns_dataframe(tmp_path):
    db_path = _make_db(tmp_path, SAMPLE_ROWS)
    result = monthly_summary(db_path)
    assert isinstance(result, pd.DataFrame)


def test_monthly_summary_has_one_row_per_month(tmp_path):
    db_path = _make_db(tmp_path, SAMPLE_ROWS)
    result = monthly_summary(db_path)
    assert sorted(result["month"]) == ["2026-01", "2026-02"]


def test_monthly_summary_nets_income_and_expense(tmp_path):
    db_path = _make_db(tmp_path, SAMPLE_ROWS)
    result = monthly_summary(db_path).set_index("month")
    # Jan: -540.20 - 85.00 + 15000.00
    assert result.loc["2026-01", "net"] == pytest.approx(14374.80)


def test_monthly_summary_uses_custom_table_name(tmp_path):
    db_path = str(tmp_path / "budget.db")
    conn = sqlite3.connect(db_path)
    pd.DataFrame(SAMPLE_ROWS).to_sql("custom_table", conn, if_exists="replace", index=False)
    conn.close()
    result = monthly_summary(db_path, table_name="custom_table")
    assert len(result) == 2