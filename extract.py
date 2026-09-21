"""
extract.py — the "E" in ETL.

Job of this file, and ONLY this file: get the raw data out of its source
(a CSV, in this project) and hand it back as a pandas DataFrame.

Rule of thumb: nothing in here should clean, fix, or re-label the data.
That belongs in transform.py. Keeping Extract "dumb on purpose" means we
can test it in isolation — its only job is "did I read the file
correctly?", not "did I get the business logic right?".
"""

import pandas as pd

DEFAULT_CSV_PATH = "data/transactions.csv"


def extract(csv_path: str = DEFAULT_CSV_PATH) -> pd.DataFrame:
    """Read the raw transactions CSV and return it as a DataFrame.

    Args:
        csv_path: Path to the CSV file to read. Defaults to the sample
            data shipped with this project.

    Returns:
        A DataFrame with the raw columns exactly as they appear in the
        CSV (date, description, amount) — no cleaning applied yet.

    Raises:
        FileNotFoundError: if csv_path doesn't exist. We let this bubble
            up rather than swallowing it, so a broken pipeline fails
            loudly at the Extract step instead of silently downstream.
    """
    df = pd.read_csv(csv_path)
    print(f"Extracted {len(df)} rows from {csv_path}")
    return df


if __name__ == "__main__":
    # Lets you sanity-check this file on its own:
    #   python3 extract.py
    data = extract()
    print(data.head())