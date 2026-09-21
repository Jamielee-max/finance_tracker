"""
transform.py — the "T" in ETL.

Takes the raw DataFrame from extract.py and turns it into something
analysis-ready:
  - real date objects instead of date-shaped text
  - a spending "category" label per transaction (keyword-based)
  - an "income" vs "expense" flag
  - a "month" column so report.py can group by month later

Nothing in here reads a file or writes to a database — pure data-in,
data-out logic. That's what makes it easy to unit test.
"""

import pandas as pd

# Keyword -> category lookup. First matching category wins, so order
# matters: more specific phrases must come before broader ones that
# they contain (e.g. "food" -> "uber eats" must be checked before
# "transport" -> "uber", or every Uber Eats transaction would get
# miscategorised as transport).
#
# Kept as a plain dict (not a class) so it's easy to read, extend, or
# eventually move into a JSON/CSV config file (see the "extend it"
# ideas in the project guide).
CATEGORY_RULES = {
    "grocery": ["checkers", "woolworths", "pick n pay", "spar"],
    "food": ["uber eats", "mr d", "takeaway", "restaurant"],
    "transport": ["uber", "bolt", "taxi", "petrol"],
    "subscriptions": ["netflix", "spotify", "showmax", "gym"],
    "shopping": ["takealot", "amazon", "superbalist"],
    "housing": ["rent", "electricity", "water", "levy"],
    "income": ["salary", "deposit", "refund"],
}


def categorise(description: str) -> str:
    """Return a category name based on keywords found in the description.

    Matching is case-insensitive and "first match wins" — if a
    description happens to match two categories, whichever appears
    first in CATEGORY_RULES is used. Anything that matches nothing
    falls back to "other" rather than raising an error, since we'd
    rather see an uncategorised transaction than crash the pipeline.
    """
    text = description.lower()
    for category, keywords in CATEGORY_RULES.items():
        if any(keyword in text for keyword in keywords):
            return category
    return "other"


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the raw DataFrame and add the derived columns report.py needs.

    Args:
        df: Raw DataFrame as returned by extract(), with at least
            'date', 'description', and 'amount' columns.

    Returns:
        A new DataFrame (the input is not mutated) with:
            date        -> real datetime64 dtype
            category    -> str, from categorise()
            type        -> "income" or "expense"
            month       -> str like "2026-01", for grouping
    """
    df = df.copy()  # never mutate the caller's DataFrame

    # 1. Make sure 'date' is a real date, not just text.
    df["date"] = pd.to_datetime(df["date"])

    # 2. Drop rows with no amount -- they're useless for analysis.
    df = df.dropna(subset=["amount"])

    # 3. Add a category column using our keyword rules.
    df["category"] = df["description"].apply(categorise)

    # 4. Add a 'type' column: income vs expense, based on the sign of amount.
    df["type"] = df["amount"].apply(lambda x: "income" if x > 0 else "expense")

    # 5. Add a 'month' column -- handy for grouping later.
    df["month"] = df["date"].dt.to_period("M").astype(str)

    print(f"Transformed {len(df)} rows")
    return df


if __name__ == "__main__":
    # Lets you sanity-check this file on its own:
    #   python3 transform.py
    from extract import extract

    raw = extract()
    clean = transform(raw)
    print(clean.head())