"""
Tests for extract.py.

We don't rely on the real data/transactions.csv here — each test
writes its own tiny throwaway CSV (via pytest's tmp_path fixture) so
these tests stay fast, isolated, and don't break if the sample data
ever changes.
"""

import pandas as pd
import pytest

from extract import extract


def _write_csv(tmp_path, contents: str) -> str:
    """Helper: write `contents` to a temp CSV file and return its path."""
    csv_path = tmp_path / "transactions.csv"
    csv_path.write_text(contents)
    return str(csv_path)


def test_extract_returns_dataframe(tmp_path):
    csv_path = _write_csv(
        tmp_path,
        "date,description,amount\n2026-01-01,Uber Trip,-50.00\n",
    )
    result = extract(csv_path)
    assert isinstance(result, pd.DataFrame)


def test_extract_reads_all_rows(tmp_path):
    csv_path = _write_csv(
        tmp_path,
        "date,description,amount\n"
        "2026-01-01,Uber Trip,-50.00\n"
        "2026-01-02,Salary Deposit,15000.00\n",
    )
    result = extract(csv_path)
    assert len(result) == 2


def test_extract_preserves_raw_columns(tmp_path):
    csv_path = _write_csv(
        tmp_path,
        "date,description,amount\n2026-01-01,Uber Trip,-50.00\n",
    )
    result = extract(csv_path)
    assert list(result.columns) == ["date", "description", "amount"]


def test_extract_does_not_add_derived_columns(tmp_path):
    """Extract should be 'dumb on purpose' -- no category/type/month yet."""
    csv_path = _write_csv(
        tmp_path,
        "date,description,amount\n2026-01-01,Uber Trip,-50.00\n",
    )
    result = extract(csv_path)
    assert "category" not in result.columns
    assert "type" not in result.columns


def test_extract_missing_file_raises(tmp_path):
    missing_path = str(tmp_path / "does_not_exist.csv")
    with pytest.raises(FileNotFoundError):
        extract(missing_path)