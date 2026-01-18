# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Portfolio Backtest is a Python tool that backtests portfolio performance based on historical stock price data. It reads transaction records from CSV, downloads historical price data from Yahoo Finance, calculates portfolio metrics, and generates a PDF report with metrics and charts.

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run with default files (transactions.csv -> report.pdf)
python -m portfolio

# Run with custom files
python -m portfolio --transactions my_transactions.csv --output my_report.pdf

# Run with sample data
python -m portfolio --transactions examples/example_transactions.csv

# Custom benchmark (default is SPY)
python -m portfolio --benchmark VT

# Disable benchmark comparison
python -m portfolio --no-benchmark

# Run with historical end date
python -m portfolio --end-date 2025-06-13
```

## Project Structure

```
portfolio/
├── __init__.py       # Package exports
├── __main__.py       # Entry point for python -m portfolio
├── models.py         # TransactionType enum, type aliases
├── data.py           # CSV loading, yfinance price fetching
├── engine.py         # Holdings history, portfolio value, normalization
├── metrics.py        # Returns, CAGR, gain/loss, benchmark metrics
├── visualization.py  # Chart generation (value, benchmark, pie)
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

1. Summary metrics (contributions, withdrawals, returns, CAGR, benchmark comparison)
2. Transactions table
3. Final holdings table
4. Portfolio value chart over time
5. Benchmark comparison chart (portfolio vs benchmark % returns)
6. Holdings pie chart

## Dependencies

- matplotlib - Chart and PDF generation
- pandas - Data manipulation
- yfinance - Yahoo Finance price data API
