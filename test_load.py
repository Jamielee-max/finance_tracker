"""
Tests for load.py.

Each test points `load()` at a throwaway SQLite file inside tmp_path,
so tests never touch the real budget.db and never leave files behind.
"""

import sqlite3

import pandas as pd

from load import load


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "date": "2026-01-01",
                "description": "Uber Trip",
                "amount": -50.0,
                "category": "transport",
                "type": "expense",
                "month": "2026-01",
            }
        ]
    )


def test_load_creates_db_file(tmp_path):
    db_path = str(tmp_path / "budget.db")
    load(_sample_df(), db_path=db_path)
    assert (tmp_path / "budget.db").exists()


def test_load_writes_correct_row_count(tmp_path):
    db_path = str(tmp_path / "budget.db")
    df = pd.concat([_sample_df()] * 3, ignore_index=True)
    load(df, db_path=db_path)

    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    conn.close()
    assert count == 3


def test_load_uses_custom_table_name(tmp_path):
    db_path = str(tmp_path / "budget.db")
    load(_sample_df(), db_path=db_path, table_name="custom_table")

    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM custom_table").fetchone()[0]
    conn.close()
    assert count == 1


def test_load_replaces_existing_table_on_rerun(tmp_path):
    """Re-running load() should rebuild the table, not duplicate rows."""
    db_path = str(tmp_path / "budget.db")
    load(_sample_df(), db_path=db_path)
    load(_sample_df(), db_path=db_path)  # run again with the same 1 row

    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    conn.close()
    assert count == 1  # not 2