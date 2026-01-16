"""Portfolio calculation engine."""

import logging

import pandas as pd

from .models import (
    HoldingsDF,
    PortfolioValueSeries,
    PricesDF,
    TransactionType,
    TransactionsDF,
)

logger = logging.getLogger(__name__)


def process_transactions(
    transactions: TransactionsDF, prices: PricesDF
) -> TransactionsDF:
    """Calculate shares for each transaction based on prices.

    Updates the 'shares' column in the transactions DataFrame.
    Returns updated transactions with shares calculated.
    """
    transactions = transactions.copy()

    for idx, row in transactions.iterrows():
        tx_date = row["date"]
        ticker = row["ticker"]
        amount = row["amount"]
        tx_type = row["type"]

        # Get price for the exact transaction date
        try:
            if tx_date not in prices.index:
                raise ValueError(
                    f"No trading data for {tx_date}. Please use a valid trading day."
                )

            price = prices.loc[tx_date, ticker]

            if pd.isna(price):
                raise ValueError(f"Price not available for {ticker} on {tx_date}")

            shares = amount / price
            if tx_type == TransactionType.SELL.value:
                shares = -shares

            transactions.at[idx, "shares"] = shares

        except KeyError:
            raise ValueError(f"No price data for {ticker} on {tx_date}")

    return transactions


def build_holdings_history(
    transactions: TransactionsDF, prices: PricesDF
) -> HoldingsDF:
    """Build a daily holdings history from transactions.

    Args:
        transactions: DataFrame with date, ticker, shares, amount, type
        prices: DataFrame with dates as index, tickers as columns

    Returns:
        DataFrame with dates as index, tickers as columns, cumulative shares as values.
    """
    # Get all trading dates from prices
    trading_dates = prices.index

    # Get all tickers
    tickers = transactions["ticker"].unique().tolist()

    # Initialize holdings DataFrame with zeros
    holdings = pd.DataFrame(0.0, index=trading_dates, columns=tickers, dtype=float)

    # Process each transaction
    for _, row in transactions.iterrows():
        tx_date = row["date"]
        ticker = row["ticker"]
        shares = row["shares"]

        if pd.isna(shares):
            continue

        # Find the first trading date on or after the transaction date
        valid_dates = [d for d in trading_dates if d >= tx_date]
        if not valid_dates:
            logger.warning(f"Transaction on {tx_date} is after all price data")
            continue
        start_date = min(valid_dates)

        # Add shares from start_date forward
        holdings.loc[start_date:, ticker] += shares

    logger.info(f"Built holdings history: {len(holdings)} days, {len(tickers)} tickers")
    return holdings


def calculate_portfolio_value(
    holdings: HoldingsDF, prices: PricesDF
) -> PortfolioValueSeries:
    """Calculate daily portfolio value.

    Args:
        holdings: DataFrame with dates as index, tickers as columns, shares as values
        prices: DataFrame with dates as index, tickers as columns, prices as values

    Returns:
        Series with dates as index, total portfolio value as values.
    """
    # Ensure holdings and prices have the same shape
    common_dates = holdings.index.intersection(prices.index)
    common_tickers = holdings.columns.intersection(prices.columns)

    holdings_aligned = holdings.loc[common_dates, common_tickers]
    prices_aligned = prices.loc[common_dates, common_tickers]

    # Calculate portfolio value: sum of (shares * price) for each ticker
    portfolio_value = (holdings_aligned * prices_aligned).sum(axis=1)
    portfolio_value.name = "portfolio_value"

    return portfolio_value


def get_current_holdings(holdings: HoldingsDF, prices: PricesDF) -> pd.DataFrame:
    """Get current holdings with values.

    Returns DataFrame with columns: ticker, shares, current_price, position_value, portfolio_pct
    """
    if holdings.empty:
        return pd.DataFrame(
            columns=[
                "ticker",
                "shares",
                "current_price",
                "position_value",
                "portfolio_pct",
            ]
        )

    # Get latest holdings
    latest_holdings = holdings.iloc[-1]
    latest_prices = prices.iloc[-1]

    # Build result DataFrame
    result = []
    for ticker in holdings.columns:
        shares = latest_holdings[ticker]
        if shares <= 0:
            continue

        price = latest_prices.get(ticker, 0)
        value = shares * price

        result.append(
            {
                "ticker": ticker,
                "shares": shares,
                "current_price": price,
                "position_value": value,
            }
        )

    if not result:
        return pd.DataFrame(
            columns=[
                "ticker",
                "shares",
                "current_price",
                "position_value",
                "portfolio_pct",
            ]
        )

    df = pd.DataFrame(result)
    total_value = df["position_value"].sum()
    df["portfolio_pct"] = (
        (df["position_value"] / total_value) * 100 if total_value > 0 else 0
    )

    # Sort by ticker
    df = df.sort_values("ticker").reset_index(drop=True)

    return df
