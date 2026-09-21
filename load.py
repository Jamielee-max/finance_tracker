"""
load.py — the "L" in ETL.

Takes the cleaned DataFrame from transform.py and writes it into a
SQLite database file. SQLite stores an entire database as one file on
disk, so there's no server to install or configure — good fit for a
small project like this one.
"""

import sqlite3

import pandas as pd

DEFAULT_DB_PATH = "budget.db"
DEFAULT_TABLE_NAME = "transactions"


def load(
    df: pd.DataFrame,
    db_path: str = DEFAULT_DB_PATH,
    table_name: str = DEFAULT_TABLE_NAME,
) -> None:
    """Write the transformed DataFrame into a SQLite table.

    Args:
        df: The cleaned DataFrame (output of transform.transform()).
        db_path: Path to the SQLite database file. Created automatically
            if it doesn't exist yet.
        table_name: Name of the table to write to.

    Note:
        if_exists="replace" means every run rebuilds the table from
        scratch instead of appending. That's the right call here since
        we always reload the *entire* source CSV — if you later move to
        incremental loading (only new rows), switch this to "append"
        and add de-duplication logic.
    """
    conn = sqlite3.connect(db_path)
    try:
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    finally:
        conn.close()
    print(f"Loaded {len(df)} rows into {db_path} -> table '{table_name}'")


if __name__ == "__main__":
    # Lets you sanity-check this file on its own:
    #   python3 load.py
    from extract import extract
    from transform import transform

    raw = extract()
    clean = transform(raw)
    load(clean)