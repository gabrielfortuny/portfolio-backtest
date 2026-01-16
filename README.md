# Portfolio Backtest

Backtest stock portfolio performance with historical price data.

## Features

- Track buys and sells from a simple CSV file
- Fetch historical prices from Yahoo Finance
- Calculate returns, CAGR, and gain/loss metrics
- Generate PDF reports with charts

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Create a `purchases.csv` file with your transactions:

```csv
date,ticker,amount,type
2020-03-16,AAPL,5000,buy
2020-06-19,MSFT,3000,buy
2023-11-15,AAPL,2000,sell
```

2. Run the backtest:

```bash
python -m portfolio.cli
```

3. Open `report.pdf` to view your results.

### Options

```
--purchases FILE    Input CSV file (default: purchases.csv)
--output FILE       Output PDF file (default: report.pdf)
--end-date DATE     End date for backtest in YYYY-MM-DD (default: today)
```

## CSV Format

| Column | Required | Description                                          |
| ------ | -------- | ---------------------------------------------------- |
| date   | Yes      | Transaction date (YYYY-MM-DD, must be a trading day) |
| ticker | Yes      | Stock symbol (e.g., AAPL, MSFT)                      |
| amount | Yes      | Dollar amount                                        |
| type   | No       | "buy" or "sell" (default: buy)                       |

## Report Contents

1. **Summary** - Contributions, withdrawals, final value, gain/loss, CAGR
2. **Transactions** - List of all buy and sell transactions
3. **Final Holdings** - Final positions with values and weights
4. **Portfolio Value Chart** - Value over time
5. **Holdings Pie Chart** - Final allocation breakdown

## License

MIT
