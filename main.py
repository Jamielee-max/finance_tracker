"""
main.py — wires the whole pipeline together: Extract -> Transform ->
Load -> Report.

Each step already has its own module and its own tests. This file has
no logic of its own to unit-test beyond "does it call the right things
in the right order and leave a populated database behind" -- that's
what test_main.py checks.
"""

from extract import extract, DEFAULT_CSV_PATH
from transform import transform
from load import load, DEFAULT_DB_PATH, DEFAULT_TABLE_NAME
from report import spending_by_category, income_vs_expense, monthly_summary


def main(
    csv_path: str = DEFAULT_CSV_PATH,
    db_path: str = DEFAULT_DB_PATH,
    table_name: str = DEFAULT_TABLE_NAME,
) -> None:
    """Run the full pipeline: read the CSV, clean it, load it into
    SQLite, then print the summary reports.

    Args:
        csv_path: Path to the raw transactions CSV.
        db_path: Path to the SQLite database to write to.
        table_name: Table name to load into.
    """
    raw = extract(csv_path)
    clean = transform(raw)
    load(clean, db_path=db_path, table_name=table_name)

    print("\nSpending by category:")
    print(spending_by_category(db_path=db_path, table_name=table_name))

    print("\nIncome vs expense:")
    print(income_vs_expense(db_path=db_path, table_name=table_name))

    print("\nMonthly summary:")
    print(monthly_summary(db_path=db_path, table_name=table_name))


if __name__ == "__main__":
    main()