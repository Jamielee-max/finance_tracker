# finance_tracker

WTC-M7E47SVN

A small personal finance / budget tracker ETL pipeline, built as a TDD project for the data engineering elective.

Reads raw transactions from a CSV, cleans and categorises them, loads them into SQLite, and prints summary reports.

## Pipeline

- **extract.py** — reads the raw transactions CSV into a DataFrame
- **transform.py** — cleans dates, categorises transactions by keyword, flags income vs expense
- **load.py** — writes the cleaned data into a SQLite database
- **report.py** — queries the database for spending by category, income vs expense, and monthly summaries
- **main.py** — runs the full pipeline end to end

## Setup

```bash
pip install pandas pytest
```

## Run the pipeline

```bash
python3 main.py
```

## Run the tests

```bash
pytest
```

## Sample output

Running `python3 main.py` against the sample data in `data/transactions.csv` prints:

```
Spending by category:
        category     total
0           food   -980.50
1        grocery  -2377.15
2        housing -22500.00
3       shopping  -2829.99
4  subscriptions  -1976.00
5      transport  -1024.50

Income vs expense:
{'income': 45350.0, 'expense': -31688.14}

Monthly summary:
     month      net
0  2026-01  4871.56
1  2026-02  4072.90
2  2026-03  4717.40
```
