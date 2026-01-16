# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Portfolio Backtest is a Python tool that backtests portfolio performance based on historical stock price data. It reads transaction records from CSV, downloads historical price data from Yahoo Finance, calculates portfolio metrics, and generates a PDF report with metrics and charts.

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run with default files (purchases.csv -> report.pdf) and end date (today)
python -m portfolio.cli

# Run with custom files
python -m portfolio.cli --purchases my_transactions.csv --output my_report.pdf

# Run with historical end date
python -m portfolio.cli --end-date 2025-06-13
```

## Project Structure

```
portfolio/
├── __init__.py       # Package exports
├── models.py         # TransactionType enum, type aliases
├── data.py           # CSV loading, yfinance price fetching
├── engine.py         # Holdings history, portfolio value calculations
├── metrics.py        # Returns, CAGR, gain/loss calculations
├── visualization.py  # Chart generation (line chart, pie chart)
├── report.py         # PDF report generation
└── cli.py            # Command-line interface
```

## Input Format

CSV with columns:

- `date` (YYYY-MM-DD) - must be a valid trading day
- `ticker` (stock symbol)
- `amount` (dollars)
- `type` (optional: "buy" or "sell", defaults to "buy")

## Output

PDF report containing:

1. Summary metrics (contributions, withdrawals, returns, CAGR)
2. Transactions table
3. Final holdings table
4. Portfolio value chart over time
5. Holdings pie chart

## Dependencies

- matplotlib - Chart and PDF generation
- pandas - Data manipulation
- yfinance - Yahoo Finance price data API
