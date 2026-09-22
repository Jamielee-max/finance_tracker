"""
Tests for main.py.

main() just wires extract -> transform -> load -> report together, so
we're not re-testing each step's logic here (that's already covered
in test_extract.py / test_transform.py / test_load.py / test_report.py).
What we ARE checking: given a CSV, running main() end-to-end leaves a
populated database behind, and calling it doesn't blow up.
"""

import sqlite3

import pandas as pd

from main import main


def _write_csv(tmp_path) -> str:
    csv_path = tmp_path / "transactions.csv"
    csv_path.write_text(
        "date,description,amount\n"
        "2026-01-03,Checkers Grocery,-540.20\n"
        "2026-01-05,Salary Deposit,15000.00\n"
    )
    return str(csv_path)


def test_main_creates_db_file(tmp_path):
    csv_path = _write_csv(tmp_path)
    db_path = str(tmp_path / "budget.db")

    main(csv_path=csv_path, db_path=db_path)

    assert (tmp_path / "budget.db").exists()


def test_main_loads_all_rows(tmp_path):
    csv_path = _write_csv(tmp_path)
    db_path = str(tmp_path / "budget.db")

    main(csv_path=csv_path, db_path=db_path)

    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    conn.close()
    assert count == 2


def test_main_applies_transform_columns(tmp_path):
    """The row that lands in the db should already be transformed
    (category/type/month present), not the raw extract() output."""
    csv_path = _write_csv(tmp_path)
    db_path = str(tmp_path / "budget.db")

    main(csv_path=csv_path, db_path=db_path)

    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    for column in ("category", "type", "month"):
        assert column in df.columns


def test_main_returns_none(tmp_path):
    """main() drives the pipeline for its side effects; it isn't
    expected to hand back a value."""
    csv_path = _write_csv(tmp_path)
    db_path = str(tmp_path / "budget.db")

    result = main(csv_path=csv_path, db_path=db_path)

    assert result is None