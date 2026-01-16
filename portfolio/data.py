"""Data loading and fetching functions for portfolio backtesting."""

import logging
from datetime import date
from pathlib import Path

import pandas as pd
import yfinance as yf

from .models import PricesDF, TransactionType, TransactionsDF

logger = logging.getLogger(__name__)


def load_transactions(path: Path) -> TransactionsDF:
    """Load transactions from CSV file.

    Expected CSV columns: date, ticker, amount
    Optional column: type (buy/sell, defaults to buy)

    Returns DataFrame with columns: date, ticker, shares, amount, type
    Note: shares will be NaN until prices are fetched and processed.
    """
    if not path.exists():
        raise FileNotFoundError(f"Transactions file not found: {path}")

    df = pd.read_csv(path)

    # Validate required columns
    required_columns = ["date", "ticker", "amount"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")

    # Parse dates
    df["date"] = pd.to_datetime(df["date"]).dt.date

    # Handle transaction type (default to buy)
    if "type" not in df.columns:
        df["type"] = TransactionType.BUY.value
    else:
        df["type"] = df["type"].str.lower()
        valid_types = {t.value for t in TransactionType}
        invalid = df[~df["type"].isin(valid_types)]["type"].unique()
        if len(invalid) > 0:
            raise ValueError(f"Invalid transaction types: {invalid}")

    # Initialize shares column (to be calculated later)
    df["shares"] = float("nan")

    # Sort by date
    df = df.sort_values("date").reset_index(drop=True)

    if df.empty:
        raise ValueError("No transactions found in file")

    logger.info(f"Loaded {len(df)} transactions from {path}")
    return df


def fetch_prices(
    tickers: list[str], start_date: date, end_date: date | None = None
) -> PricesDF:
    """Fetch historical price data from Yahoo Finance.

    Args:
        tickers: List of stock ticker symbols
        start_date: Start date for price history
        end_date: End date for price history (defaults to today)

    Returns:
        DataFrame with dates as index, tickers as columns, closing prices as values.
    """
    if end_date is None:
        end_date = date.today()

    logger.info(
        f"Fetching prices for {len(tickers)} tickers from {start_date} to {end_date}"
    )

    # Download data from yfinance
    data = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        progress=False,
    )

    if data is None or data.empty:
        raise ValueError("Failed to fetch price data from Yahoo Finance")

    # Extract closing prices
    if len(tickers) == 1:
        # Single ticker returns Series, convert to DataFrame
        prices = pd.DataFrame({tickers[0]: data["Close"]})
    else:
        prices = data["Close"]

    # Ensure all requested tickers are present
    missing_tickers = set(tickers) - set(prices.columns)
    if missing_tickers:
        raise ValueError(f"Failed to fetch prices for tickers: {missing_tickers}")

    # Convert index to date (not datetime)
    prices.index = prices.index.date

    logger.info(f"Fetched {len(prices)} days of price data")
    return prices
