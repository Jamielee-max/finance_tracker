"""
report.py — turns the loaded SQLite data into summaries someone
actually wants to read.

Three views, each answering one question:
    spending_by_category() -> "where is my money going?"
    income_vs_expense()    -> "am I net positive or negative?"
    monthly_summary()      -> "how does that change month to month?"

Nothing in here writes to the database -- read-only queries against
whatever load.py already wrote.
"""

import sqlite3

import pandas as pd

from load import DEFAULT_DB_PATH, DEFAULT_TABLE_NAME


def spending_by_category(
    db_path: str = DEFAULT_DB_PATH,
    table_name: str = DEFAULT_TABLE_NAME,
) -> pd.DataFrame:
    """Total amount spent per category, expenses only.

    Returns:
        DataFrame with columns ['category', 'total'], one row per
        expense category. 'income' is excluded since it isn't a
        spending category. 'total' stays negative (it's a sum of
        expense amounts) so it sorts naturally biggest-spend-first
        with .sort_values('total').
    """
    conn = sqlite3.connect(db_path)
    try:
        query = f"""
            SELECT category, SUM(amount) AS total
            FROM {table_name}
            WHERE type = 'expense'
            GROUP BY category
        """
        result = pd.read_sql_query(query, conn)
    finally:
        conn.close()
    return result


def income_vs_expense(
    db_path: str = DEFAULT_DB_PATH,
    table_name: str = DEFAULT_TABLE_NAME,
) -> dict:
    """Total income and total expense across all transactions.

    Returns:
        {"income": <float>, "expense": <float>}. Either key defaults
        to 0 if that type never appears in the data, rather than
        raising -- a data set with no income yet is valid, not broken.
    """
    conn = sqlite3.connect(db_path)
    try:
        query = f"""
            SELECT type, SUM(amount) AS total
            FROM {table_name}
            GROUP BY type
        """
        rows = pd.read_sql_query(query, conn)
    finally:
        conn.close()

    totals = dict(zip(rows["type"], rows["total"]))
    return {
        "income": totals.get("income", 0),
        "expense": totals.get("expense", 0),
    }


def monthly_summary(
    db_path: str = DEFAULT_DB_PATH,
    table_name: str = DEFAULT_TABLE_NAME,
) -> pd.DataFrame:
    """Net cash flow per month (income + expense, expense already negative).

    Returns:
        DataFrame with columns ['month', 'net'], one row per month
        that appears in the data.
    """
    conn = sqlite3.connect(db_path)
    try:
        query = f"""
            SELECT month, SUM(amount) AS net
            FROM {table_name}
            GROUP BY month
            ORDER BY month
        """
        result = pd.read_sql_query(query, conn)
    finally:
        conn.close()
    return result


if __name__ == "__main__":
    # Lets you sanity-check this file on its own, against the real
    # pipeline output:
    #   python3 extract.py && python3 transform.py  (or run the full
    #   pipeline once main.py exists) then:
    #   python3 report.py
    print("Spending by category:")
    print(spending_by_category())
    print("\nIncome vs expense:")
    print(income_vs_expense())
    print("\nMonthly summary:")
    print(monthly_summary())