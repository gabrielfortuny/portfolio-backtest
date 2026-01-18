# Portfolio Backtest

Backtest stock portfolio performance with historical price data.

## Features

- Track buys and sells from a simple CSV file
- Fetch historical prices from Yahoo Finance
- Calculate returns, CAGR, and gain/loss metrics
- Compare performance against a benchmark (default: SPY)
- Generate PDF reports with charts

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Create a `transactions.csv` file with your transactions:

```csv
date,ticker,amount,type
2020-03-16,AAPL,5000,buy
2020-06-19,MSFT,3000,buy
2023-11-15,AAPL,2000,sell
```

2. Run the backtest:

```bash
python -m portfolio
```

3. Open `report.pdf` to view your results.

### Options

```
--transactions FILE   Input CSV file (default: transactions.csv)
--output FILE         Output PDF file (default: report.pdf)
--end-date DATE       End date for backtest in YYYY-MM-DD (default: today)
--benchmark TICKER    Benchmark for comparison (default: SPY)
--no-benchmark        Disable benchmark comparison
```

### Examples

```bash
# Use the example file
python -m portfolio --transactions examples/example_transactions.csv

# Compare against VT instead of SPY
python -m portfolio --benchmark VT

# Skip benchmark comparison
python -m portfolio --no-benchmark
```

## CSV Format

| Column | Required | Description                                          |
| ------ | -------- | ---------------------------------------------------- |
| date   | Yes      | Transaction date (YYYY-MM-DD, must be a trading day) |
| ticker | Yes      | Stock symbol (e.g., AAPL, MSFT)                      |
| amount | Yes      | Dollar amount                                        |
| type   | No       | "buy" or "sell" (default: buy)                       |

## Report Contents

1. **Summary** - Contributions, withdrawals, final value, gain/loss, CAGR, benchmark comparison
2. **Transactions** - List of all buy and sell transactions
3. **Final Holdings** - Final positions with values and weights
4. **Portfolio Value Chart** - Value over time
5. **Benchmark Comparison Chart** - Portfolio vs benchmark returns over time
6. **Holdings Pie Chart** - Final allocation breakdown

## License

MIT
