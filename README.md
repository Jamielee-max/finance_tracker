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